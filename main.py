"""
main.py
Main entry point for AQI Prediction System
"""

import argparse
import logging
from config.config import LOGGING_LEVEL

# Configure logging
logging.basicConfig(
    level=LOGGING_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='AQI Prediction System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --dashboard          # Run Streamlit dashboard
  python main.py --api fastapi        # Run FastAPI server
  python main.py --api flask          # Run Flask server
  python main.py --train lstm         # Train LSTM model
  python main.py --train ensemble     # Train ensemble model
        """
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Run Streamlit dashboard'
    )
    
    parser.add_argument(
        '--api',
        choices=['fastapi', 'flask'],
        help='Run API server'
    )
    
    parser.add_argument(
        '--train',
        choices=['lstm', 'ensemble'],
        help='Train selected model'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run tests'
    )
    
    args = parser.parse_args()
    
    if args.dashboard:
        logger.info("Starting Streamlit dashboard...")
        import subprocess
        subprocess.run(['streamlit', 'run', 'src/apps/dashboard.py'])
    
    elif args.api:
        if args.api == 'fastapi':
            logger.info("Starting FastAPI server...")
            import subprocess
            subprocess.run(
                ['uvicorn', 'src.apps.api.fastapi_app:app', 
                 '--reload', '--host', '0.0.0.0', '--port', '8000']
            )
        else:
            logger.info("Starting Flask server...")
            from src.apps.api.flask_app import app
            app.run(host='0.0.0.0', port=5000, debug=True)
    
    elif args.train:
        if args.train == 'lstm':
            logger.info("Training LSTM model...")
            from src.models_ml.lstm_model import LSTMAQIPredictor
            # Training code here
            logger.info("Model training not implemented via CLI")
        else:
            logger.info("Training Ensemble model...")
            from src.models_ml.ensemble_model import AQIEnsemble
            # Training code here
            logger.info("Model training not implemented via CLI")
    
    elif args.test:
        logger.info("Running tests...")
        import subprocess
        subprocess.run(['pytest', 'tests/', '-v'])
    
    else:
        logger.info("AQI Prediction System - Usage:")
        parser.print_help()


if __name__ == '__main__':
    main()
