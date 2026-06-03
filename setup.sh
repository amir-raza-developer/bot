#!/bin/bash
echo "🔧 Installing SMBot..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt || { echo "❌ pip install failed"; exit 1; }

echo "🌐 Installing Playwright Chromium..."
playwright install chromium || { echo "❌ Playwright install failed"; exit 1; }
playwright install-deps chromium 2>/dev/null || true   # Linux only, OK to ignore on Windows/Mac

echo "🗄️  Running migrations..."
cd backend
python manage.py migrate || { echo "❌ Migration failed"; exit 1; }

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

echo ""
echo "✅ Setup complete!"
echo "🚀 Start the bot:  cd backend && python manage.py runserver"
echo "📖 Then open:      http://localhost:8000"
