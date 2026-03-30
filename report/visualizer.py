"""Visualization utilities for VLM-ARB reports."""

from __future__ import annotations

from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


class BenchmarkVisualizer:
    """Creates visualizations for benchmark results."""
    
    def __init__(self, style: str = "seaborn-v0_8-darkgrid"):
        """
        Initialize visualizer.
        
        Args:
            style: Matplotlib style name
        """
        plt.style.use(style)
        self.figures = []
    
    def plot_model_comparison(self, model_scores: Dict) -> plt.Figure:
        """
        Create bar chart comparing model robustness scores.
        
        Args:
            model_scores: Dict mapping model_id to robustness score
        
        Returns:
            Matplotlib figure
        
        """
        if not model_scores:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.set_title("Model Robustness Comparison")
            ax.text(0.5, 0.5, "No model data available", ha="center", va="center")
            ax.axis("off")
            return fig

        sorted_items = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        models = [m for m, _ in sorted_items]
        scores = [float(s) for _, s in sorted_items]

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = ["#2E8B57" if s >= 0.7 else "#D4A017" if s >= 0.5 else "#B22222" for s in scores]
        bars = ax.bar(models, scores, color=colors, alpha=0.9)

        ax.set_ylim(0, 1)
        ax.set_ylabel("Robustness Score")
        ax.set_title("Model Robustness Comparison")
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", linestyle="--", alpha=0.3)

        for bar, score in zip(bars, scores):
            ax.text(bar.get_x() + bar.get_width() / 2, min(score + 0.02, 0.99), f"{score:.2f}", ha="center", va="bottom", fontsize=9)

        fig.tight_layout()
        return fig
    
    def plot_attack_effectiveness(self, attack_asr: Dict) -> plt.Figure:
        """
        Create bar chart showing effectiveness of each attack type.
        
        Args:
            attack_asr: Dict mapping attack_type to average ASR
        
        Returns:
            Matplotlib figure
        
        """
        if not attack_asr:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.set_title("Attack Effectiveness")
            ax.text(0.5, 0.5, "No attack data available", ha="center", va="center")
            ax.axis("off")
            return fig

        sorted_items = sorted(attack_asr.items(), key=lambda x: x[1], reverse=True)
        attacks = [a for a, _ in sorted_items]
        asr_values = [float(v) for _, v in sorted_items]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(attacks, asr_values, color="#C0392B", alpha=0.85)
        ax.set_ylim(0, 1)
        ax.set_ylabel("Attack Effectiveness (higher = worse for model)")
        ax.set_title("Attack Effectiveness by Type")
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", linestyle="--", alpha=0.3)

        for bar, val in zip(bars, asr_values):
            ax.text(bar.get_x() + bar.get_width() / 2, min(val + 0.02, 0.99), f"{val:.2f}", ha="center", va="bottom", fontsize=9)

        fig.tight_layout()
        return fig
    
    def plot_modality_dominance(self, cmcs_by_model: Dict) -> plt.Figure:
        """
        Create profile showing vision vs language dominance per model.
        
        Args:
            cmcs_by_model: Dict mapping model_id to average CMCS score
        
        Returns:
            Matplotlib figure
        
        """
        if not cmcs_by_model:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.set_title("Modality Dominance")
            ax.text(0.5, 0.5, "CMCS data not available", ha="center", va="center")
            ax.axis("off")
            return fig

        sorted_items = sorted(cmcs_by_model.items(), key=lambda x: x[1])
        models = [m for m, _ in sorted_items]
        values = [float(v) for _, v in sorted_items]

        fig, ax = plt.subplots(figsize=(10, 5))
        y_positions = list(range(len(models)))
        ax.scatter(values, y_positions, color="#1F77B4", s=80)
        ax.axvline(0.0, color="#444444", linestyle="--", linewidth=1)

        for idx, (model, val) in enumerate(zip(models, values)):
            ax.text(val + (0.02 if val >= 0 else -0.02), idx, model, va="center", ha="left" if val >= 0 else "right", fontsize=9)

        ax.set_yticks(y_positions)
        ax.set_yticklabels([""] * len(models))
        ax.set_xlabel("CMCS (negative=vision-dominant, positive=language-dominant)")
        ax.set_title("Cross-Modal Dominance Profile")
        ax.grid(axis="x", linestyle="--", alpha=0.3)

        fig.tight_layout()
        return fig
    
    def plot_transferability_heatmap(self, transfer_matrix: Dict[str, Dict]) -> plt.Figure:
        """
        Create heatmap of attack transferability between models.
        
        Args:
            transfer_matrix: Dict[model_from][model_to] = transfer_rate
        
        Returns:
            Matplotlib figure with heatmap
        
        """
        if not transfer_matrix:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.set_title("Attack Transferability")
            ax.text(0.5, 0.5, "Transferability data not available", ha="center", va="center")
            ax.axis("off")
            return fig

        frame = pd.DataFrame(transfer_matrix).T.fillna(0.0)
        frame = frame.reindex(sorted(frame.index), axis=0)
        frame = frame.reindex(sorted(frame.columns), axis=1)

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(frame, annot=True, fmt=".2f", cmap="Reds", vmin=0, vmax=1, linewidths=0.5, cbar_kws={"label": "Transfer Rate"}, ax=ax)
        ax.set_title("Attack Transferability Matrix")
        ax.set_xlabel("Target Model")
        ax.set_ylabel("Source Model")

        fig.tight_layout()
        return fig
