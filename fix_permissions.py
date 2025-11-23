#!/usr/bin/env python3
"""
Script pour corriger automatiquement les permissions des endpoints
"""

import re

# Mapping des routes vers les modules et leurs permissions
ROUTE_TO_MODULE = {
    # Work Orders
    r'/work-orders': ('workOrders', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Equipment
    r'/equipments': ('assets', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Locations
    r'/locations': ('locations', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Inventory
    r'/inventory': ('inventory', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Preventive Maintenance
    r'/preventive-maintenance': ('preventiveMaintenance', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Intervention Requests
    r'/intervention-requests': ('interventionRequests', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Improvement Requests
    r'/improvement-requests': ('improvementRequests', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Improvements
    r'/improvements': ('improvements', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Meters
    r'/meters': ('meters', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Surveillance
    r'/surveillance': ('surveillance', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Presqu'accident
    r'/presqu-accident': ('presquaccident', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Documentations
    r'/documentations': ('documentations', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Vendors
    r'/vendors': ('vendors', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Reports
    r'/reports': ('reports', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Users/People
    r'/users': ('people', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Planning
    r'/planning': ('planning', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Purchase History
    r'/purchase-history': ('purchaseHistory', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Import/Export
    r'/import-export': ('importExport', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
    
    # Availabilities
    r'/availabilities': ('workOrders', {'GET': 'view', 'POST': 'edit', 'PUT': 'edit', 'DELETE': 'delete'}),
}

# Routes qui doivent rester avec get_current_user (auth, profile, etc.)
AUTH_ROUTES = [
    r'/auth/me',
    r'/auth/change-password',
    r'/auth/forgot-password',
    r'/auth/reset-password',
    r'/auth/validate-invitation',
    r'/auth/complete-registration',
    r'/auth/change-password-first-login',
    r'/user-preferences',
]

# Routes qui nécessitent get_current_admin_user
ADMIN_ROUTES = [
    r'/users/invite-member',
    r'/users/create-member',
    r'/settings',
    r'/smtp/config',
    r'/users/.*/permissions',
    r'/users/default-permissions',
]

def should_skip_route(route):
    """Vérifie si la route doit être ignorée"""
    for auth_route in AUTH_ROUTES:
        if re.search(auth_route, route):
            return True
    return False

def is_admin_route(route):
    """Vérifie si la route nécessite des droits admin"""
    for admin_route in ADMIN_ROUTES:
        if re.search(admin_route, route):
            return True
    return False

def get_module_and_permission(route, http_method):
    """Trouve le module et la permission pour une route donnée"""
    for route_pattern, (module, permissions) in ROUTE_TO_MODULE.items():
        if re.search(route_pattern, route):
            permission = permissions.get(http_method, 'view')
            return module, permission
    return None, None

def analyze_server_file():
    """Analyse le fichier server.py et génère les corrections"""
    with open('/app/backend/server.py', 'r') as f:
        content = f.read()
    
    # Pattern pour trouver les endpoints
    endpoint_pattern = r'@api_router\.(get|post|put|delete)\("([^"]+)"\)[\s\S]*?async def ([a-zA-Z_]+)\(([^)]+)\):'
    
    matches = re.finditer(endpoint_pattern, content)
    
    corrections = []
    
    for match in matches:
        http_method = match.group(1).upper()
        route = match.group(2)
        func_name = match.group(3)
        params = match.group(4)
        
        # Ignorer les routes d'auth
        if should_skip_route(route):
            continue
        
        # Si utilise déjà require_permission, ignorer
        if 'require_permission' in params:
            continue
        
        # Si utilise get_current_admin_user, ignorer (déjà correct)
        if 'get_current_admin_user' in params:
            continue
        
        # Si utilise get_current_user
        if 'Depends(get_current_user)' in params:
            if is_admin_route(route):
                corrections.append({
                    'route': route,
                    'method': http_method,
                    'func': func_name,
                    'old': 'Depends(get_current_user)',
                    'new': 'Depends(get_current_admin_user)',
                    'type': 'admin'
                })
            else:
                module, permission = get_module_and_permission(route, http_method)
                if module and permission:
                    corrections.append({
                        'route': route,
                        'method': http_method,
                        'func': func_name,
                        'old': 'Depends(get_current_user)',
                        'new': f'Depends(require_permission("{module}", "{permission}"))',
                        'type': 'permission',
                        'module': module,
                        'permission': permission
                    })
    
    return corrections

if __name__ == '__main__':
    print("🔍 Analyse des endpoints...")
    corrections = analyze_server_file()
    
    print(f"\n📊 {len(corrections)} endpoints à corriger:\n")
    
    for i, correction in enumerate(corrections, 1):
        print(f"{i}. {correction['method']} {correction['route']}")
        print(f"   Fonction: {correction['func']}")
        if correction['type'] == 'admin':
            print(f"   Correction: {correction['old']} → {correction['new']}")
        else:
            print(f"   Module: {correction['module']}, Permission: {correction['permission']}")
            print(f"   Correction: {correction['old']} → {correction['new']}")
        print()
    
    print(f"\n✅ Analyse terminée. {len(corrections)} corrections nécessaires.")
