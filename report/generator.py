"""Report generation for VLM-ARB benchmark results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from statistics import mean
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Tuple

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .visualizer import BenchmarkVisualizer


@dataclass
class AttackSummary:
    attack_name: str
    models: Dict[str, Dict[str, float]] = field(default_factory=dict)
    failure_examples: List[Dict[str, Any]] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def attack_effectiveness(self) -> Optional[float]:
        values: List[float] = []
        for metrics in self.models.values():
            if "attack_effectiveness" in metrics:
                values.append(float(metrics["attack_effectiveness"]))
            elif "accuracy_drop_abs" in metrics:
                values.append(max(0.0, float(metrics["accuracy_drop_abs"])))
            elif "prediction_change_rate" in metrics:
                values.append(float(metrics["prediction_change_rate"]))
        if not values:
            return None
        return mean(values)

    def model_robustness_scores(self) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for model_name, metrics in self.models.items():
            if "robustness_score" in metrics:
                scores[model_name] = float(metrics["robustness_score"])
                continue

            if "perturbed_accuracy" in metrics:
                scores[model_name] = float(metrics["perturbed_accuracy"])
                continue

            attack_effectiveness = metrics.get("attack_effectiveness")
            if attack_effectiveness is None and "prediction_change_rate" in metrics:
                attack_effectiveness = metrics["prediction_change_rate"]
            if attack_effectiveness is not None:
                scores[model_name] = 1.0 - float(attack_effectiveness)

        return scores


class ReportGenerator:
    """Generates benchmark reports in PDF and HTML formats."""
    
    def __init__(self, results_dir: str, output_dir: str = "results/reports"):
        """
        Initialize report generator.
        
        Args:
            results_dir: Directory with raw JSON results
            output_dir: Directory to save generated reports
        """
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.visualizer = BenchmarkVisualizer()
        self.expected_attacks = ["typographic", "perturbation", "prompt_injection", "patch", "crossmodal"]

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _read_json(self, path: Path) -> Any:
        with path.open("r", encoding="utf-8") as file_obj:
            return json.load(file_obj)

    def _infer_attack_from_name(self, file_name: str) -> str:
        lower_name = file_name.lower()
        for attack in self.expected_attacks:
            if attack in lower_name:
                return attack
        if "local_robustness" in lower_name or "perturb" in lower_name:
            return "perturbation"
        if "typo" in lower_name:
            return "typographic"
        return "unknown"

    def _parse_local_robustness(self, payload: Dict[str, Any], source: str) -> Optional[AttackSummary]:
        if not isinstance(payload, dict) or "results" not in payload:
            return None

        results = payload.get("results")
        if not isinstance(results, dict) or not results:
            return None

        attack_name = str(payload.get("attack_type") or self._infer_attack_from_name(source))
        summary = AttackSummary(attack_name=attack_name, source_files=[source])
        summary.metadata = {
            "num_images": payload.get("num_images"),
            "clean_dir": payload.get("clean_dir"),
            "perturbed_dir": payload.get("perturbed_dir"),
            "device": payload.get("device"),
        }

        for model_name, model_metrics in results.items():
            if not isinstance(model_metrics, dict):
                continue

            prediction_change_rate = model_metrics.get("prediction_change_rate")
            target_hit_rate = model_metrics.get("target_hit_rate")

            # Typographic/other local runs can be change-rate based and may not have accuracy fields.
            if prediction_change_rate is not None:
                change_rate = self._safe_float(prediction_change_rate)
                clean_acc_raw = model_metrics.get("clean_accuracy")
                pert_acc_raw = model_metrics.get("perturbed_accuracy")
                clean_acc = None if clean_acc_raw is None else self._safe_float(clean_acc_raw)
                pert_acc = None if pert_acc_raw is None else self._safe_float(pert_acc_raw)

                model_payload: Dict[str, float] = {
                    "num_pairs": self._safe_float(model_metrics.get("num_pairs")),
                    "prediction_change_rate": change_rate,
                    "attack_effectiveness": change_rate,
                    "robustness_score": max(0.0, min(1.0, 1.0 - change_rate)),
                }

                if target_hit_rate is not None:
                    model_payload["target_hit_rate"] = self._safe_float(target_hit_rate)
                if clean_acc is not None:
                    model_payload["clean_accuracy"] = clean_acc
                if pert_acc is not None:
                    model_payload["perturbed_accuracy"] = pert_acc

                if clean_acc is not None and pert_acc is not None:
                    drop_abs = self._safe_float(model_metrics.get("accuracy_drop_abs"), clean_acc - pert_acc)
                    drop_pp = self._safe_float(model_metrics.get("accuracy_drop_pct_points"), drop_abs * 100.0)
                    model_payload["accuracy_drop_abs"] = drop_abs
                    model_payload["accuracy_drop_pct_points"] = drop_pp

                summary.models[model_name] = model_payload
                continue

            clean_acc = self._safe_float(model_metrics.get("clean_accuracy"))
            pert_acc = self._safe_float(model_metrics.get("perturbed_accuracy"))
            drop_abs = self._safe_float(model_metrics.get("accuracy_drop_abs"), clean_acc - pert_acc)
            drop_pp = self._safe_float(model_metrics.get("accuracy_drop_pct_points"), drop_abs * 100.0)

            summary.models[model_name] = {
                "clean_accuracy": clean_acc,
                "perturbed_accuracy": pert_acc,
                "accuracy_drop_abs": drop_abs,
                "accuracy_drop_pct_points": drop_pp,
                "attack_effectiveness": max(0.0, drop_abs),
                "robustness_score": max(0.0, min(1.0, pert_acc)),
            }

        return summary if summary.models else None

    def _parse_typographic_report(self, payload: Any, source: str) -> Optional[AttackSummary]:
        if not isinstance(payload, list) or not payload:
            return None
        if not isinstance(payload[0], dict) or "prediction_change_rate" not in payload[0]:
            return None

        summary = AttackSummary(attack_name="typographic", source_files=[source])

        for row in payload:
            if not isinstance(row, dict):
                continue
            if row.get("error"):
                continue

            model_name = str(row.get("model", "unknown_model"))
            change_rate = self._safe_float(row.get("prediction_change_rate"))
            target_hit_rate = row.get("target_hit_rate")
            target_hit_rate = None if target_hit_rate is None else self._safe_float(target_hit_rate)

            summary.models[model_name] = {
                "num_pairs": self._safe_float(row.get("num_pairs")),
                "prediction_change_rate": change_rate,
                "target_hit_rate": target_hit_rate if target_hit_rate is not None else -1.0,
                "attack_effectiveness": change_rate,
                "robustness_score": max(0.0, min(1.0, 1.0 - change_rate)),
                "avg_conf_original": self._safe_float(row.get("avg_conf_original")),
                "avg_conf_poison": self._safe_float(row.get("avg_conf_poison")),
            }

            details = row.get("details") or []
            if isinstance(details, list):
                for item in details:
                    if not isinstance(item, dict):
                        continue
                    if item.get("prediction_changed") is True:
                        summary.failure_examples.append(
                            {
                                "model": model_name,
                                "sample": item.get("filename", "unknown"),
                                "clean_pred": item.get("original_pred", ""),
                                "attacked_pred": item.get("poison_pred", ""),
                                "target_label": item.get("target_label", ""),
                            }
                        )

        return summary if summary.models else None

    def _parse_generic_rows(self, payload: Any, source: str, attack_name: str) -> Optional[AttackSummary]:
        if not isinstance(payload, list) or not payload:
            return None
        if not isinstance(payload[0], dict):
            return None

        first_row = payload[0]
        if "model_id" not in first_row and "model_name" not in first_row:
            return None

        grouped: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for row in payload:
            if not isinstance(row, dict):
                continue
            model_name = str(row.get("model_name") or row.get("model_id") or "unknown_model")
            row_attack = str(row.get("attack") or row.get("attack_type") or attack_name)
            key = (row_attack, model_name)
            grouped.setdefault(key, []).append(row)

        by_attack: Dict[str, AttackSummary] = {}
        for (row_attack, model_name), rows in grouped.items():
            summary = by_attack.setdefault(row_attack, AttackSummary(attack_name=row_attack, source_files=[source]))

            asr_values = [self._safe_float(r.get("asr")) for r in rows if r.get("asr") is not None]
            ods_values = [self._safe_float(r.get("ods")) for r in rows if r.get("ods") is not None]
            error_count = sum(1 for r in rows if r.get("error"))

            attack_effectiveness = mean(asr_values) if asr_values else None
            if attack_effectiveness is None and ods_values:
                attack_effectiveness = min(1.0, max(0.0, mean(ods_values)))

            model_metrics = {
                "num_samples": float(len(rows)),
                "error_rate": (error_count / len(rows)) if rows else 0.0,
                "asr": mean(asr_values) if asr_values else -1.0,
                "ods": mean(ods_values) if ods_values else -1.0,
            }

            if attack_effectiveness is not None:
                model_metrics["attack_effectiveness"] = attack_effectiveness
                model_metrics["robustness_score"] = max(0.0, min(1.0, 1.0 - attack_effectiveness))

            summary.models[model_name] = model_metrics

            for row in rows:
                if row.get("error"):
                    continue
                clean_out = str(row.get("clean_output", "")).strip()
                attack_out = str(row.get("attacked_output", "")).strip()
                if clean_out and attack_out and clean_out != attack_out:
                    summary.failure_examples.append(
                        {
                            "model": model_name,
                            "sample": row.get("image_id", "unknown"),
                            "clean_pred": clean_out[:60],
                            "attacked_pred": attack_out[:60],
                            "target_label": "",
                        }
                    )

        candidates = [v for k, v in by_attack.items() if k != "unknown" and v.models]
        if not candidates and attack_name != "unknown":
            default_summary = by_attack.get(attack_name)
            if default_summary and default_summary.models:
                return default_summary
            return None
        if len(candidates) == 1:
            return candidates[0]
        return None

    def _discover_summaries(self) -> Dict[str, AttackSummary]:
        results_path = Path(self.results_dir)
        if not results_path.exists():
            return {}

        summaries: Dict[str, AttackSummary] = {}
        json_files = sorted(results_path.rglob("*.json"))

        for json_file in json_files:
            try:
                payload = self._read_json(json_file)
            except Exception:
                continue

            source = str(json_file)
            parsed = self._parse_local_robustness(payload, source)
            if parsed is None:
                parsed = self._parse_typographic_report(payload, source)
            if parsed is None:
                inferred = self._infer_attack_from_name(json_file.name)
                parsed = self._parse_generic_rows(payload, source, inferred)

            if parsed is None:
                continue

            existing = summaries.get(parsed.attack_name)
            if existing is None:
                summaries[parsed.attack_name] = parsed
                continue

            existing.source_files.extend(parsed.source_files)
            for model_name, metrics in parsed.models.items():
                existing.models[model_name] = metrics
            existing.failure_examples.extend(parsed.failure_examples)
            existing.metadata.update(parsed.metadata)

        return summaries

    def _build_executive_summary(self, attacks: Dict[str, AttackSummary]) -> Dict[str, Any]:
        if not attacks:
            return {
                "num_attacks": 0,
                "num_models": 0,
                "strongest_attack": None,
                "most_vulnerable_model": None,
            }

        attack_effectiveness: Dict[str, float] = {}
        model_vulnerability: Dict[str, List[float]] = {}

        for attack_name, summary in attacks.items():
            effectiveness = summary.attack_effectiveness()
            if effectiveness is not None:
                attack_effectiveness[attack_name] = effectiveness

            for model_name, metrics in summary.models.items():
                vulnerability = metrics.get("attack_effectiveness")
                if vulnerability is not None:
                    model_vulnerability.setdefault(model_name, []).append(float(vulnerability))

        strongest_attack = None
        if attack_effectiveness:
            strongest_attack = max(attack_effectiveness.items(), key=lambda x: x[1])

        vulnerable_model = None
        if model_vulnerability:
            vulnerable_model = max(((m, mean(v)) for m, v in model_vulnerability.items()), key=lambda x: x[1])

        all_models = {model for attack in attacks.values() for model in attack.models.keys()}
        return {
            "num_attacks": len(attacks),
            "num_models": len(all_models),
            "strongest_attack": strongest_attack,
            "most_vulnerable_model": vulnerable_model,
        }

    def _save_figure(self, fig, output_path: Path) -> str:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=160, bbox_inches="tight")
        fig.clf()
        return str(output_path)

    @staticmethod
    def _make_table(data: List[List[str]], col_widths: Optional[List[float]] = None) -> Table:
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF9")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F7F7")]),
                ]
            )
        )
        return table
    
    def generate_pdf_report(self, title: str = "VLM-ARB Benchmark Report",
                           include_sections: List[str] = None) -> str:
        """
        Generate a PDF report.
        
        Args:
            title: Report title
            include_sections: Sections to include in report
                             (default: all)
        
        Returns:
            Path to generated PDF file
        
        """
        include_sections = include_sections or ["summary", "charts", "details", "failures"]
        attacks = self._discover_summaries()

        output_dir = Path(self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"vlm_benchmark_report_{timestamp}.pdf"

        doc = SimpleDocTemplate(str(report_path), pagesize=A4)
        styles = getSampleStyleSheet()
        story: List[Any] = []

        summary = self._build_executive_summary(attacks)
        missing_attacks = [a for a in self.expected_attacks if a not in attacks]

        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        story.append(Paragraph(f"Results source: {Path(self.results_dir).resolve()}", styles["Normal"]))
        story.append(Spacer(1, 12))

        if "summary" in include_sections:
            story.append(Paragraph("Executive Summary", styles["Heading2"]))
            story.append(Paragraph(f"Attacks with usable data: {summary['num_attacks']}", styles["Normal"]))
            story.append(Paragraph(f"Unique models evaluated: {summary['num_models']}", styles["Normal"]))

            strongest = summary["strongest_attack"]
            if strongest:
                story.append(Paragraph(f"Most effective attack: {strongest[0]} ({strongest[1]:.3f})", styles["Normal"]))

            vulnerable = summary["most_vulnerable_model"]
            if vulnerable:
                story.append(Paragraph(f"Most vulnerable model overall: {vulnerable[0]} ({vulnerable[1]:.3f})", styles["Normal"]))

            if missing_attacks:
                story.append(Paragraph(f"Skipped attacks (missing/not implemented/no data): {', '.join(missing_attacks)}", styles["Normal"]))

            story.append(Spacer(1, 12))

        with TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)

            if "charts" in include_sections and attacks:
                story.append(Paragraph("Global Charts", styles["Heading2"]))
                attack_effectiveness = {
                    attack_name: attack_summary.attack_effectiveness()
                    for attack_name, attack_summary in attacks.items()
                    if attack_summary.attack_effectiveness() is not None
                }
                if attack_effectiveness:
                    fig = self.visualizer.plot_attack_effectiveness(attack_effectiveness)
                    chart_path = self._save_figure(fig, temp_root / "attack_effectiveness.png")
                    story.append(Image(chart_path, width=480, height=250))
                    story.append(Spacer(1, 8))

                combined_model_scores: Dict[str, List[float]] = {}
                for attack_summary in attacks.values():
                    for model_name, score in attack_summary.model_robustness_scores().items():
                        combined_model_scores.setdefault(model_name, []).append(score)

                model_scores_avg = {name: mean(values) for name, values in combined_model_scores.items() if values}
                if model_scores_avg:
                    fig = self.visualizer.plot_model_comparison(model_scores_avg)
                    chart_path = self._save_figure(fig, temp_root / "global_model_scores.png")
                    story.append(Image(chart_path, width=480, height=250))

                story.append(PageBreak())

            for attack_name in sorted(attacks.keys()):
                attack = attacks[attack_name]
                story.append(Paragraph(f"Attack: {attack_name}", styles["Heading2"]))
                if attack.source_files:
                    story.append(Paragraph(f"Sources: {', '.join(sorted(set(attack.source_files)))}", styles["Normal"]))
                story.append(Spacer(1, 6))

                if "details" in include_sections:
                    table_rows = [["Model", "Robustness", "Attack Effectiveness", "Drop/ASR", "Extra"]]
                    for model_name, metrics in sorted(attack.models.items()):
                        robustness = metrics.get("robustness_score")
                        effectiveness = metrics.get("attack_effectiveness")
                        drop = metrics.get("accuracy_drop_abs")
                        if drop is None:
                            drop = metrics.get("prediction_change_rate")
                        if drop is None:
                            drop = metrics.get("asr")

                        extra = ""
                        if "perturbed_accuracy" in metrics:
                            extra = f"Pert Acc={metrics['perturbed_accuracy']:.3f}"
                        elif "target_hit_rate" in metrics and metrics["target_hit_rate"] >= 0:
                            extra = f"Target Hit={metrics['target_hit_rate']:.3f}"
                        elif "ods" in metrics and metrics["ods"] >= 0:
                            extra = f"ODS={metrics['ods']:.3f}"

                        table_rows.append(
                            [
                                model_name,
                                f"{robustness:.3f}" if robustness is not None else "N/A",
                                f"{effectiveness:.3f}" if effectiveness is not None else "N/A",
                                f"{drop:.3f}" if drop is not None and drop >= 0 else "N/A",
                                extra,
                            ]
                        )

                    story.append(self._make_table(table_rows, col_widths=[120, 90, 120, 90, 120]))
                    story.append(Spacer(1, 10))

                if "charts" in include_sections:
                    model_scores = attack.model_robustness_scores()
                    if model_scores:
                        fig = self.visualizer.plot_model_comparison(model_scores)
                        chart_path = self._save_figure(fig, temp_root / f"{attack_name}_models.png")
                        story.append(Image(chart_path, width=470, height=235))
                        story.append(Spacer(1, 8))

                if "failures" in include_sections:
                    if attack.failure_examples:
                        story.append(Paragraph("Where Models Fail (Top Examples)", styles["Heading3"]))
                        fail_rows = [["Model", "Sample", "Clean Output", "Attacked Output", "Target"]]
                        for item in attack.failure_examples[:10]:
                            fail_rows.append(
                                [
                                    str(item.get("model", ""))[:22],
                                    str(item.get("sample", ""))[:24],
                                    str(item.get("clean_pred", ""))[:34],
                                    str(item.get("attacked_pred", ""))[:34],
                                    str(item.get("target_label", ""))[:18],
                                ]
                            )
                        story.append(self._make_table(fail_rows, col_widths=[85, 95, 120, 120, 55]))
                        story.append(Spacer(1, 8))
                    else:
                        story.append(Paragraph("No sample-level failure rows were available for this attack.", styles["Normal"]))
                        story.append(Spacer(1, 8))

                story.append(PageBreak())

            if not attacks:
                story.append(Paragraph("No valid result files were discovered. Add JSON outputs under the results directory and regenerate.", styles["Normal"]))

            doc.build(story)
        return str(report_path)
    
    def generate_html_report(self, title: str = "VLM-ARB Benchmark Report",
                            include_interactive: bool = True) -> str:
        """
        Generate an HTML report (can include interactive plots).
        
        Args:
            title: Report title
            include_interactive: Include plotly interactive charts (default: True)
        
        Returns:
            Path to generated HTML file
        """
        attacks = self._discover_summaries()
        summary = self._build_executive_summary(attacks)

        output_dir = Path(self.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"vlm_benchmark_report_{timestamp}.html"

        rows: List[str] = []
        for attack_name, attack in sorted(attacks.items()):
            rows.append(f"<h2>Attack: {attack_name}</h2>")
            rows.append("<table border='1' cellspacing='0' cellpadding='6'>")
            rows.append("<tr><th>Model</th><th>Robustness</th><th>Attack Effectiveness</th></tr>")
            for model_name, metrics in sorted(attack.models.items()):
                robustness = metrics.get("robustness_score")
                effectiveness = metrics.get("attack_effectiveness")
                rows.append(
                    "<tr>"
                    f"<td>{model_name}</td>"
                    f"<td>{'N/A' if robustness is None else f'{robustness:.3f}'}</td>"
                    f"<td>{'N/A' if effectiveness is None else f'{effectiveness:.3f}'}</td>"
                    "</tr>"
                )
            rows.append("</table>")

        skipped = [a for a in self.expected_attacks if a not in attacks]
        html = (
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "  <meta charset=\"UTF-8\" />\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n"
            f"  <title>{title}</title>\n"
            "</head>\n"
            "<body style=\"font-family: Arial, sans-serif; margin: 2rem;\">\n"
            f"  <h1>{title}</h1>\n"
            f"  <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n"
            "  <h2>Executive Summary</h2>\n"
            f"  <p>Attacks with data: {summary['num_attacks']}</p>\n"
            f"  <p>Unique models: {summary['num_models']}</p>\n"
            f"  <p>Skipped attacks: {', '.join(skipped) if skipped else 'None'}</p>\n"
            f"  {''.join(rows)}\n"
            "</body>\n"
            "</html>\n"
        )
        report_path.write_text(html, encoding="utf-8")
        return str(report_path)
