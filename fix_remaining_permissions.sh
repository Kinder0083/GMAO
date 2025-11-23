#!/bin/bash
# Script pour corriger les permissions restantes

SERVER_FILE="/app/backend/server.py"

echo "🔧 Correction des permissions restantes..."

# Availabilities - planning module
sed -i 's/\/availabilities")\s*$\nasync def get_availabilities(\([^)]*\)current_user: dict = Depends(get_current_user)/\/availabilities")\nasync def get_availabilities(\1current_user: dict = Depends(require_permission("planning", "view"))/g' "$SERVER_FILE" 2>/dev/null || echo "Skip availabilities GET"

# Purchase History
sed -i 's/@api_router\.get("\/purchase-history")\nasync def get_purchase_history_grouped(current_user: dict = Depends(get_current_user))/@api_router.get("\/purchase-history")\nasync def get_purchase_history_grouped(current_user: dict = Depends(require_permission("purchaseHistory", "view")))/g' "$SERVER_FILE" 2>/dev/null || echo "Skip purchase GET"

sed -i 's/async def create_purchase(purchase: PurchaseHistoryCreate, current_user: dict = Depends(get_current_user))/async def create_purchase(purchase: PurchaseHistoryCreate, current_user: dict = Depends(require_permission("purchaseHistory", "edit")))/g' "$SERVER_FILE"

sed -i 's/async def update_purchase(purchase_id: str, purchase_update: PurchaseHistoryUpdate, current_user: dict = Depends(get_current_user))/async def update_purchase(purchase_id: str, purchase_update: PurchaseHistoryUpdate, current_user: dict = Depends(require_permission("purchaseHistory", "edit")))/g' "$SERVER_FILE"

# Meters
sed -i 's/async def get_all_meters(current_user: dict = Depends(get_current_user))/async def get_all_meters(current_user: dict = Depends(require_permission("meters", "view")))/g' "$SERVER_FILE"

sed -i 's/async def get_meter(meter_id: str, current_user: dict = Depends(get_current_user))/async def get_meter(meter_id: str, current_user: dict = Depends(require_permission("meters", "view")))/g' "$SERVER_FILE"

echo "✅ Corrections terminées"
echo "📊 Vérification..."
grep -c "Depends(get_current_user)" "$SERVER_FILE" | xargs -I {} echo "Reste {} occurrences de get_current_user"
grep -c "require_permission" "$SERVER_FILE" | xargs -I {} echo "Total {} vérifications de permissions"
