#!/usr/bin/env python3
"""
Interactive AE Visualizer

A Flask-based web application for interactive visualization of AE optimization results.
Allows users to select individual runs and view detailed visualizations.
"""

from flask import Flask, render_template, jsonify, request, send_file
import json
import os
from pathlib import Path
from datetime import datetime
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

app = Flask(__name__)

class InteractiveVisualizer:
    """Interactive visualization handler for AE optimization results"""
    
    def __init__(self, outputs_path: str = "outputs"):
        self.outputs_path = Path(outputs_path)
        self.runs_cache = {}
        self._load_all_runs()
    
    def _load_all_runs(self) -> None:
        """Load metadata for all available runs"""
        if not self.outputs_path.exists():
            return
            
        run_dirs = [d for d in self.outputs_path.iterdir() 
                   if d.is_dir() and d.name.startswith('run_')]
        
        for run_dir in sorted(run_dirs):
            try:
                run_data = self._load_run_metadata(run_dir)
                if run_data:
                    self.runs_cache[run_dir.name] = run_data
            except Exception as e:
                print(f"Error loading {run_dir.name}: {e}")
    
    def _load_run_metadata(self, run_dir: Path) -> Optional[Dict]:
        """Load metadata for a single run"""
        best_params_file = run_dir / "best_parameters.json"
        config_file = run_dir / "config.json"
        readme_file = run_dir / "README.md"
        
        if not all([best_params_file.exists(), config_file.exists()]):
            return None
            
        with open(best_params_file, 'r') as f:
            best_params_data = json.load(f)
            
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Parse timestamp
        timestamp_str = run_dir.name.replace('run_', '')
        timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        
        # Check available plots
        plots_available = []
        for plot_file in ['optimization_progress.png', 'feature_importance.png']:
            if (run_dir / plot_file).exists():
                plots_available.append(plot_file)
        
        return {
            'run_id': run_dir.name,
            'timestamp': timestamp.isoformat(),
            'timestamp_formatted': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'config': config_data,
            'parameters': best_params_data.get('parameters', {}),
            'metrics': best_params_data.get('metrics', {}),
            'timing_stats': best_params_data.get('timing_stats', {}),
            'trial_results': best_params_data.get('trial_results_summary', {}),
            'plots_available': plots_available,
            'path': str(run_dir)
        }
    
    def get_runs_list(self) -> List[Dict]:
        """Get list of all available runs with summary info"""
        runs = []
        for run_id, run_data in self.runs_cache.items():
            # Extract key metrics
            soft_f1 = run_data['metrics'].get('soft_f1_score', [None])[0] or 0
            soft_recall = run_data['metrics'].get('soft_recall', [None])[0] or 0
            soft_precision = run_data['metrics'].get('soft_precision', [None])[0] or 0
            
            runs.append({
                'run_id': run_id,
                'timestamp': run_data['timestamp_formatted'],
                'soft_f1': round(soft_f1, 4),
                'soft_recall': round(soft_recall, 4),
                'soft_precision': round(soft_precision, 4),
                'num_trials': run_data['config'].get('AE_NUM_TRIALS', 0),
                'ensemble_size': run_data['config'].get('N_ENSEMBLE_GROUP_NUMBER', 0),
                'training_mode': 'Parallel' if run_data['config'].get('PARALLEL_TRAINING', False) else 'Sequential',
                'avg_trial_time': round(run_data['timing_stats'].get('average_trial_time_seconds', 0), 1),
                'plots_available': run_data['plots_available']
            })
        
        return sorted(runs, key=lambda x: x['timestamp'], reverse=True)
    
    def get_run_details(self, run_id: str) -> Optional[Dict]:
        """Get detailed information for a specific run"""
        return self.runs_cache.get(run_id)
    
    def create_performance_plot(self, run_id: str) -> str:
        """Create interactive performance plot using Plotly"""
        run_data = self.runs_cache.get(run_id)
        if not run_data:
            return ""
        
        metrics = run_data['metrics']
        
        # Create gauge plots for main metrics
        fig = go.Figure()
        
        # Soft F1 Score
        soft_f1 = metrics.get('soft_f1_score', [0])[0] or 0
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = soft_f1,
            domain = {'x': [0, 0.3], 'y': [0, 1]},
            title = {'text': "Soft F1 Score"},
            gauge = {
                'axis': {'range': [None, 1]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 0.5], 'color': "lightgray"},
                    {'range': [0.5, 0.8], 'color': "gray"},
                    {'range': [0.8, 1], 'color': "lightgreen"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.85}}))
        
        # Soft Recall
        soft_recall = metrics.get('soft_recall', [0])[0] or 0
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = soft_recall,
            domain = {'x': [0.35, 0.65], 'y': [0, 1]},
            title = {'text': "Soft Recall"},
            gauge = {
                'axis': {'range': [None, 1]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 0.5], 'color': "lightgray"},
                    {'range': [0.5, 0.8], 'color': "gray"},
                    {'range': [0.8, 1], 'color': "lightgreen"}]}))
        
        # Soft Precision
        soft_precision = metrics.get('soft_precision', [0])[0] or 0
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = soft_precision,
            domain = {'x': [0.7, 1], 'y': [0, 1]},
            title = {'text': "Soft Precision"},
            gauge = {
                'axis': {'range': [None, 1]},
                'bar': {'color': "darkorange"},
                'steps': [
                    {'range': [0, 0.5], 'color': "lightgray"},
                    {'range': [0.5, 0.8], 'color': "gray"},
                    {'range': [0.8, 1], 'color': "lightgreen"}]}))
        
        fig.update_layout(
            title=f"Performance Metrics - {run_id}",
            height=400,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_parameters_plot(self, run_id: str) -> str:
        """Create interactive parameters visualization"""
        run_data = self.runs_cache.get(run_id)
        if not run_data:
            return ""
        
        params = run_data['parameters']
        
        # Key parameters to visualize
        key_params = ['learning_rate', 'num_leaves', 'max_depth', 'n_estimators', 
                     'subsample', 'colsample_bytree', 'reg_alpha', 'reg_lambda']
        
        param_names = []
        param_values = []
        
        for param in key_params:
            if param in params:
                param_names.append(param.replace('_', ' ').title())
                param_values.append(params[param])
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=param_names,
                x=param_values,
                orientation='h',
                marker_color='lightblue',
                text=param_values,
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title=f"Key Parameters - {run_id}",
            xaxis_title="Parameter Value",
            yaxis_title="Parameters",
            height=400,
            margin=dict(l=120, r=20, t=60, b=20)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def create_timing_plot(self, run_id: str) -> str:
        """Create timing analysis visualization"""
        run_data = self.runs_cache.get(run_id)
        if not run_data:
            return ""
        
        timing_stats = run_data['timing_stats']
        config = run_data['config']
        
        # Create timing breakdown
        labels = ['Average Trial Time', 'Min Trial Time', 'Max Trial Time']
        values = [
            timing_stats.get('average_trial_time_seconds', 0),
            timing_stats.get('min_trial_time_seconds', 0),
            timing_stats.get('max_trial_time_seconds', 0)
        ]
        
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=values,
                marker_color=['skyblue', 'lightgreen', 'lightcoral'],
                text=[f"{v:.1f}s" for v in values],
                textposition='outside'
            )
        ])
        
        # Add configuration info as annotation
        config_text = f"""Configuration:
Trials: {config.get('AE_NUM_TRIALS', 'N/A')}
Ensemble Size: {config.get('N_ENSEMBLE_GROUP_NUMBER', 'N/A')}
Mode: {'Parallel' if config.get('PARALLEL_TRAINING', False) else 'Sequential'}
Total Time: {timing_stats.get('total_trial_time_seconds', 0):.1f}s"""
        
        fig.add_annotation(
            x=1, y=max(values) * 0.8,
            text=config_text,
            showarrow=False,
            align="left",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1
        )
        
        fig.update_layout(
            title=f"Timing Analysis - {run_id}",
            yaxis_title="Time (seconds)",
            height=400,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)

# Global visualizer instance
visualizer = InteractiveVisualizer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/runs')
def get_runs():
    """API endpoint to get all runs list"""
    return jsonify(visualizer.get_runs_list())

@app.route('/api/run/<run_id>')
def get_run_details(run_id):
    """API endpoint to get detailed run information"""
    run_data = visualizer.get_run_details(run_id)
    if not run_data:
        return jsonify({'error': 'Run not found'}), 404
    return jsonify(run_data)

@app.route('/api/plot/performance/<run_id>')
def get_performance_plot(run_id):
    """API endpoint to get performance plot"""
    plot_json = visualizer.create_performance_plot(run_id)
    return jsonify({'plot': plot_json})

@app.route('/api/plot/parameters/<run_id>')
def get_parameters_plot(run_id):
    """API endpoint to get parameters plot"""
    plot_json = visualizer.create_parameters_plot(run_id)
    return jsonify({'plot': plot_json})

@app.route('/api/plot/timing/<run_id>')
def get_timing_plot(run_id):
    """API endpoint to get timing plot"""
    plot_json = visualizer.create_timing_plot(run_id)
    return jsonify({'plot': plot_json})

@app.route('/api/image/<run_id>/<filename>')
def get_run_image(run_id, filename):
    """Serve run-specific images (optimization_progress.png, feature_importance.png)"""
    run_data = visualizer.get_run_details(run_id)
    if not run_data:
        return "Run not found", 404
    
    # Convert to absolute path to ensure correct file location
    image_path = Path(run_data['path']).resolve() / filename
    if not image_path.exists():
        return "Image not found", 404
    
    return send_file(str(image_path))

@app.route('/compare')
def compare_runs():
    """Comparison page for multiple runs"""
    return render_template('compare.html')

@app.route('/api/compare', methods=['POST'])
def compare_runs_api():
    """API endpoint for run comparison"""
    try:
        # Validate request
        if not request.json:
            return jsonify({'error': 'Invalid JSON request'}), 400
            
        run_ids = request.json.get('run_ids', [])
        
        if not run_ids or len(run_ids) < 2:
            return jsonify({'error': 'At least 2 run IDs required for comparison'}), 400
        
        print(f"Comparing runs: {run_ids}")  # Debug logging
        
        comparison_data = []
        for run_id in run_ids:
            run_data = visualizer.get_run_details(run_id)
            if run_data:
                try:
                    # Extract key metrics for comparison with better error handling
                    metrics = run_data.get('metrics', {})
                    timing_stats = run_data.get('timing_stats', {})
                    config = run_data.get('config', {})
                    
                    # Handle different possible metric formats
                    soft_f1 = 0
                    soft_recall = 0
                    soft_precision = 0
                    
                    if 'soft_f1_score' in metrics:
                        soft_f1_val = metrics['soft_f1_score']
                        if isinstance(soft_f1_val, list) and len(soft_f1_val) > 0:
                            soft_f1 = soft_f1_val[0] or 0
                        elif isinstance(soft_f1_val, (int, float)):
                            soft_f1 = soft_f1_val
                    
                    if 'soft_recall' in metrics:
                        soft_recall_val = metrics['soft_recall']
                        if isinstance(soft_recall_val, list) and len(soft_recall_val) > 0:
                            soft_recall = soft_recall_val[0] or 0
                        elif isinstance(soft_recall_val, (int, float)):
                            soft_recall = soft_recall_val
                    
                    if 'soft_precision' in metrics:
                        soft_precision_val = metrics['soft_precision']
                        if isinstance(soft_precision_val, list) and len(soft_precision_val) > 0:
                            soft_precision = soft_precision_val[0] or 0
                        elif isinstance(soft_precision_val, (int, float)):
                            soft_precision = soft_precision_val
                    
                    comparison_data.append({
                        'run_id': run_id,
                        'timestamp': run_data.get('timestamp_formatted', 'Unknown'),
                        'soft_f1': round(float(soft_f1), 4),
                        'soft_recall': round(float(soft_recall), 4),
                        'soft_precision': round(float(soft_precision), 4),
                        'num_trials': config.get('AE_NUM_TRIALS', 0),
                        'ensemble_size': config.get('N_ENSEMBLE_GROUP_NUMBER', 0),
                        'avg_trial_time': round(timing_stats.get('average_trial_time_seconds', 0), 1),
                        'training_mode': 'Parallel' if config.get('PARALLEL_TRAINING', False) else 'Sequential'
                    })
                    
                except Exception as e:
                    print(f"Error processing run {run_id}: {e}")
                    continue
            else:
                print(f"Run data not found for: {run_id}")
        
        # Create comparison plot
        if comparison_data and len(comparison_data) >= 2:
            try:
                df = pd.DataFrame(comparison_data)
                
                # Performance comparison plot
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df['run_id'],
                    y=df['soft_f1'],
                    mode='lines+markers',
                    name='Soft F1',
                    line=dict(color='blue', width=3),
                    marker=dict(size=8)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['run_id'],
                    y=df['soft_recall'],
                    mode='lines+markers',
                    name='Soft Recall',
                    line=dict(color='green', width=3),
                    marker=dict(size=8)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df['run_id'],
                    y=df['soft_precision'],
                    mode='lines+markers',
                    name='Soft Precision',
                    line=dict(color='orange', width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="Performance Comparison Across Selected Runs",
                    xaxis_title="Run ID",
                    yaxis_title="Score",
                    height=400,
                    margin=dict(l=20, r=20, t=60, b=40),
                    xaxis={'tickangle': 45}
                )
                
                plot_json = json.dumps(fig, cls=PlotlyJSONEncoder)
                
                return jsonify({
                    'comparison_data': comparison_data,
                    'plot': plot_json
                })
                
            except Exception as e:
                print(f"Error creating comparison plot: {e}")
                return jsonify({'error': f'Error creating comparison plot: {str(e)}'}), 500
        
        return jsonify({'error': f'Insufficient valid runs found for comparison. Found {len(comparison_data)} valid runs from {len(run_ids)} requested.'}), 400
        
    except Exception as e:
        print(f"Error in compare_runs_api: {e}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

def create_app():
    """Create and configure the Flask application"""
    return app

def main():
    """Main entry point for the web interface"""
    print("Starting Interactive AE Visualizer...")
    print("Access the application at: http://localhost:5001")
    app.run(debug=True, port=5001, host='0.0.0.0')

if __name__ == '__main__':
    main()