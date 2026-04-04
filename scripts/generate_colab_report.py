#!/usr/bin/env python3
"""
Generate reports from Colab-imported results.

Takes the results imported from Colab and generates interactive HTML and PDF reports
for local viewing without re-running tests.

Usage:
    python generate_colab_report.py
    python generate_colab_report.py --input results/colab_imported/colab_results_normalized.json
    python generate_colab_report.py --input results/colab_imported/ --format html
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import statistics

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class ColabReportGenerator:
    """Generate reports from Colab-imported results."""
    
    def __init__(self, output_dir: str = "results/colab_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
    
    def load_results(self, input_path: str) -> bool:
        """
        Load results from file or directory.
        
        Args:
            input_path: Path to JSON file or results directory
            
        Returns:
            True if results loaded successfully
        """
        input_file = Path(input_path)
        
        if input_file.is_file() and input_file.suffix == '.json':
            print(f"📄 Loading JSON: {input_file}")
            with open(input_file, 'r') as f:
                self.results = json.load(f)
            print(f"✓ Loaded {len(self.results)} result items")
            return True
        
        elif input_file.is_dir():
            # Look for normalized JSON in directory
            norm_file = input_file / "colab_results_normalized.json"
            if norm_file.exists():
                print(f"📂 Loading from directory: {input_file}")
                with open(norm_file, 'r') as f:
                    self.results = json.load(f)
                print(f"✓ Loaded {len(self.results)} result items")
                return True
            else:
                print(f"❌ No colab_results_normalized.json found in {input_file}")
                return False
        
        else:
            print(f"❌ File not found: {input_file}")
            return False
    
    def generate_html(self, output_name: str = "report") -> str:
        """
        Generate interactive HTML report.
        
        Args:
            output_name: Name of output file (without extension)
            
        Returns:
            Path to generated HTML file
        """
        if not self.results:
            print("❌ No results loaded. Call load_results() first.")
            return ""
        
        html_file = self.output_dir / f"{output_name}.html"
        
        print(f"\n📝 Generating HTML report...")
        
        # Extract metrics from results
        metrics_summary = self._extract_metrics()
        
        # Generate HTML content
        html_content = self._build_html(metrics_summary)
        
        # Write to file
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✓ Generated: {html_file}")
        return str(html_file)
    
    def generate_pdf(self, output_name: str = "report") -> Optional[str]:
        """
        Generate PDF report.
        
        Args:
            output_name: Name of output file (without extension)
            
        Returns:
            Path to generated PDF file, or None if reportlab not installed
        """
        if not HAS_REPORTLAB:
            print("⚠️  reportlab not installed. Skipping PDF generation.")
            print("   Install with: pip install reportlab")
            return None
        
        if not self.results:
            print("❌ No results loaded. Call load_results() first.")
            return None
        
        pdf_file = self.output_dir / f"{output_name}.pdf"
        
        print(f"\n📄 Generating PDF report...")
        
        # Extract metrics
        metrics_summary = self._extract_metrics()
        
        # Build PDF
        doc = SimpleDocTemplate(
            str(pdf_file),
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=12,
            alignment=1
        )
        elements.append(Paragraph("Colab Image Injection Results", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Metadata
        timestamp = self.results.get("metadata", {}).get("timestamp", "Unknown")
        elements.append(Paragraph(f"<b>Generated:</b> {timestamp}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Metrics summary table
        if metrics_summary:
            elements.append(Paragraph("<b>Attack Success Rates by Model</b>", styles['Heading2']))
            table_data = [["Model", "ASR (%)", "Count"]]
            
            for model, metrics in metrics_summary.items():
                asr = metrics.get("asr", 0)
                count = metrics.get("count", 0)
                table_data.append([model, f"{asr:.1f}", str(count)])
            
            table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(table)
        
        # Build PDF
        try:
            doc.build(elements)
            print(f"✓ Generated: {pdf_file}")
            return str(pdf_file)
        except Exception as e:
            print(f"❌ PDF generation failed: {e}")
            return None
    
    def _extract_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Extract summary metrics from results.
        
        Returns:
            Dictionary of metrics by model
        """
        metrics = {}
        
        # Parse results looking for model-level metrics
        if isinstance(self.results, dict):
            for key, value in self.results.items():
                if isinstance(value, dict):
                    # Try to extract model metrics
                    if "model" in value:
                        model_name = value["model"]
                        if model_name not in metrics:
                            metrics[model_name] = {
                                "asr": 0,
                                "count": 0,
                                "attacks": []
                            }
                        
                        # Look for ASR
                        if "asr" in value:
                            metrics[model_name]["asr"] = float(value["asr"]) * 100
                        elif "attack_success_rate" in value:
                            metrics[model_name]["asr"] = float(value["attack_success_rate"]) * 100
                        
                        metrics[model_name]["count"] += 1
        
        return metrics
    
    def _build_html(self, metrics: Dict[str, Dict[str, float]]) -> str:
        """
        Build HTML report content.
        
        Args:
            metrics: Extracted metrics dictionary
            
        Returns:
            HTML string
        """
        timestamp = self.results.get("metadata", {}).get("timestamp", "Unknown")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Colab Image Injection Results</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 5px;
        }}
        
        .metric-card h3 {{
            color: #333;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .metric-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        table th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #667eea;
        }}
        
        table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        
        table tr:hover {{
            background: #f8f9fa;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            background: #e9ecef;
            border-radius: 3px;
            font-size: 0.85em;
            color: #495057;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 Image Injection Attack Evaluation</h1>
            <p>Results imported from Google Colab • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            <h2>📊 Summary Statistics</h2>
            <div class="metrics-grid">
"""
        
        # Add metric cards
        all_asr_values = [m["asr"] for m in metrics.values() if "asr" in m]
        total_tests = sum(m["count"] for m in metrics.values())
        avg_asr = statistics.mean(all_asr_values) if all_asr_values else 0
        
        html += f"""
                <div class="metric-card">
                    <h3>Models Tested</h3>
                    <div class="value">{len(metrics)}</div>
                </div>
                <div class="metric-card">
                    <h3>Total Tests</h3>
                    <div class="value">{total_tests}</div>
                </div>
                <div class="metric-card">
                    <h3>Average ASR</h3>
                    <div class="value">{avg_asr:.1f}%</div>
                </div>
            </div>
            
            <h2>📈 Results by Model</h2>
            <table>
                <thead>
                    <tr>
                        <th>Model</th>
                        <th>Attack Success Rate</th>
                        <th>Tests Run</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Add table rows
        for model, metrics_data in sorted(metrics.items()):
            asr = metrics_data.get("asr", 0)
            count = metrics_data.get("count", 0)
            html += f"""
                    <tr>
                        <td><span class="badge">{model}</span></td>
                        <td>{asr:.1f}%</td>
                        <td>{count}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>✅ Results loaded from: <strong>Colab Image Injection Notebook</strong></p>
            <p>Generated with: <strong>generate_colab_report.py</strong></p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def print_summary(self):
        """Print text summary of results."""
        print("\n" + "=" * 60)
        print("📊 RESULTS SUMMARY")
        print("=" * 60)
        
        metrics = self._extract_metrics()
        
        if metrics:
            print(f"\n✓ Found metrics for {len(metrics)} models:")
            for model, data in metrics.items():
                asr = data.get("asr", 0)
                count = data.get("count", 0)
                print(f"   {model:20s} - ASR: {asr:6.1f}% ({count} tests)")
        else:
            print("\n⚠️  No metrics found in results")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Generate reports from Colab-imported results"
    )
    
    parser.add_argument(
        "--input",
        type=str,
        default="results/colab_imported",
        help="Input JSON file or directory with results"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/colab_reports",
        help="Output directory for generated reports"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["html", "pdf", "both"],
        default="both",
        help="Report format to generate"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="report",
        help="Output filename (without extension)"
    )
    
    args = parser.parse_args()
    
    generator = ColabReportGenerator(output_dir=args.output)
    
    # Load results
    if not generator.load_results(args.input):
        print("❌ Failed to load results")
        sys.exit(1)
    
    # Print summary
    generator.print_summary()
    
    # Generate reports
    print(f"\n📋 Generating reports...")
    
    if args.format in ["html", "both"]:
        html_path = generator.generate_html(args.name)
        if html_path:
            print(f"   💻 Open in browser: {html_path}")
    
    if args.format in ["pdf", "both"]:
        pdf_path = generator.generate_pdf(args.name)
        if pdf_path:
            print(f"   📄 View PDF: {pdf_path}")
        elif args.format == "pdf":
            print("   ⚠️  PDF generation requires reportlab")
    
    print("\n✅ Report generation complete!")


if __name__ == "__main__":
    main()
