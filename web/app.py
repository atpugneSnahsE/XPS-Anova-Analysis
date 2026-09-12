import os
import sys
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, current_app
from flask_cors import CORS
import logging

app = Flask(__name__, template_folder='templates')
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory and web directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

try:
    from web_api import process_xps_file, process_anova_file, detect_analysis_type
except ImportError as e:
    logger.warning(f"Could not import web_api: {e}")
    # Fallback functions if imports fail
    def process_xps_file(file_path, output_dir):
        raise NotImplementedError("XPS processing not available")
    def process_anova_file(file_path, output_dir):
        raise NotImplementedError("ANOVA processing not available")
    def detect_analysis_type(file_path):
        return 'unknown'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/downloads')
def downloads():
    """Show downloads page with available releases"""
    return render_template('downloads.html')


@app.route('/releases')
def releases():
    """Redirect to downloads"""
    return downloads()


@app.route('/release/<filename>')
def download_release(filename):
    """Download a release file"""
    try:
        releases_dir = Path(__file__).parent.parent / 'downloads'
        file_path = releases_dir / secure_filename(filename)

        if not file_path.exists() or not str(file_path).endswith('.zip'):
            return jsonify({'error': 'Release not found'}), 404

        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.exception("Release download error")
        return jsonify({'error': 'Download failed'}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Handle file upload and run analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        analysis_type = request.form.get('type', 'auto')

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only Excel files (.xlsx, .xls) allowed'}), 400

        # Create temporary directories
        temp_dir = tempfile.mkdtemp()
        work_dir = os.path.join(temp_dir, 'work')
        results_dir = os.path.join(temp_dir, 'results')
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)

        # Save uploaded file
        filename = secure_filename(file.filename)
        input_path = os.path.join(work_dir, filename)
        file.save(input_path)

        logger.info(f"Processing file: {filename}")

        # Determine analysis type and run
        results = {'status': 'success', 'files': [], 'summary': {}}

        if analysis_type in ['auto', 'xps']:
            try:
                logger.info("Running XPS analysis...")
                xps_results = run_xps_analysis(input_path, work_dir, results_dir)
                results['xps'] = xps_results
                results['files'].extend(xps_results.get('files', []))
            except Exception as e:
                logger.error(f"XPS analysis failed: {str(e)}")
                if analysis_type == 'xps':
                    return jsonify({'error': f'XPS analysis failed: {str(e)}'}), 500

        if analysis_type in ['auto', 'anova']:
            try:
                logger.info("Running ANOVA analysis...")
                anova_results = run_anova_analysis(input_path, work_dir, results_dir)
                results['anova'] = anova_results
                results['files'].extend(anova_results.get('files', []))
            except Exception as e:
                logger.error(f"ANOVA analysis failed: {str(e)}")
                if analysis_type == 'anova':
                    return jsonify({'error': f'ANOVA analysis failed: {str(e)}'}), 500

        # Create results ZIP
        zip_path = os.path.join(temp_dir, 'results.zip')
        create_results_zip(results_dir, zip_path)

        # Clean up and return
        logger.info(f"Analysis complete. Results: {zip_path}")

        return jsonify({
            'status': 'success',
            'download_url': f'/api/download/{os.path.basename(temp_dir)}',
            'results': results
        })

    except Exception as e:
        logger.exception("Unexpected error during analysis")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


def run_xps_analysis(file_path, work_dir, results_dir):
    """Run XPS peak analysis"""
    try:
        result = process_xps_file(file_path, results_dir)

        # Collect output files
        output_files = []
        xps_dir = Path(results_dir) / "xps_results"
        if xps_dir.exists():
            for root, dirs, files in os.walk(xps_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    output_files.append(os.path.relpath(file_path, results_dir))

        return {
            'status': 'completed',
            'peaks_found': result.get('peaks_found', 0),
            'files': output_files
        }
    except Exception as e:
        logger.exception("XPS analysis failed")
        raise


def run_anova_analysis(file_path, work_dir, results_dir):
    """Run ANOVA analysis"""
    try:
        result = process_anova_file(file_path, results_dir)

        # Collect output files
        output_files = []
        anova_dir = Path(results_dir) / "anova_results"
        if anova_dir.exists():
            for root, dirs, files in os.walk(anova_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    output_files.append(os.path.relpath(file_path, results_dir))

        return {
            'status': 'completed',
            'files': output_files
        }
    except Exception as e:
        logger.exception("ANOVA analysis failed")
        raise


def create_results_zip(results_dir, zip_path):
    """Create ZIP file of all results"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(results_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, results_dir)
                zipf.write(file_path, arcname)


@app.route('/api/download/<session_id>')
def download_results(session_id):
    """Download results ZIP file"""
    try:
        zip_path = os.path.join(tempfile.gettempdir(), session_id, 'results.zip')
        if os.path.exists(zip_path):
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=f'anova_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
            )
        return jsonify({'error': 'Results not found'}), 404
    except Exception as e:
        logger.exception("Download error")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
