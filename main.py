import os
import sys

# Add backend directory to path
sys.path.insert(0, 'backend')

# Import and run the backend app
if __name__ == "__main__":
    os.chdir('backend')
    from app import app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001))) 