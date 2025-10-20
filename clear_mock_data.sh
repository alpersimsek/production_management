#!/bin/bash
# Clear all mock data from Vue pages

echo "🧹 Clearing all mock data from frontend pages..."

# Clear mock data arrays in Vue files
find /home/alper/factory_prod_management/frontend/src/pages -name "*.vue" -exec sed -i 's/= ref(\[[^]]*\])/= ref([])/g' {} \;

# Clear mock data comments
find /home/alper/factory_prod_management/frontend/src/pages -name "*.vue" -exec sed -i 's/\/\/ Mock data for now/\/\/ Load data from API/g' {} \;

echo "✅ Mock data cleared from all pages!"
echo "📱 Dashboard and all pages now show empty data"
echo "💡 Add data through the frontend interface"
