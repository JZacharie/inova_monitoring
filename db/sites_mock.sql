-- Mock data for Inova Monitoring Service Catalog
-- Sites: Geel, Core Model, Lyon
-- Environments: dev, val, prod

INSERT INTO instances (name, url, environment, region, datacenter, version, owner_po, owner_tech, owner_business, maintenance_windows, argocd_app_name, argocd_url, latitude, longitude)
VALUES 
-- Geel (Belgium)
('Geel Dev', 'https://geel-dev.inova-software.com', 'dev', 'Europe-West', 'OpenShift-BE', 'v4.0.0-alpha', 'PO Geel', 'Tech Geel', 'Biz Geel', 'N/A', 'geel-dev', 'https://argocd.inova.local/applications/geel-dev', 51.1606, 4.9904),
('Geel Val', 'https://geel-val.inova-software.com', 'val', 'Europe-West', 'OpenShift-BE', 'v3.9.5', 'PO Geel', 'Tech Geel', 'Biz Geel', 'Wednesdays 18:00-20:00 UTC', 'geel-val', 'https://argocd.inova.local/applications/geel-val', 51.1606, 4.9904),
('Geel Prod', 'https://geel.inova-software.com', 'prod', 'Europe-West', 'OpenShift-BE', 'v3.9.0', 'PO Geel', 'Tech Geel', 'Biz Geel', 'Sundays 02:00-04:00 UTC', 'geel-prod', 'https://argocd.inova.local/applications/geel-prod', 51.1606, 4.9904),

-- Core Model (Central/France)
('Core Model Dev', 'https://core-dev.inova-software.com', 'dev', 'Europe-West', 'OpenShift-FR', 'v4.0.0-alpha', 'PO Core', 'Tech Core', 'Biz Core', 'N/A', 'core-dev', 'https://argocd.inova.local/applications/core-dev', 48.8566, 2.3522),
('Core Model Val', 'https://core-val.inova-software.com', 'val', 'Europe-West', 'OpenShift-FR', 'v3.9.5', 'PO Core', 'Tech Core', 'Biz Core', 'Wednesdays 18:00-20:00 UTC', 'core-val', 'https://argocd.inova.local/applications/core-val', 48.8566, 2.3522),
('Core Model Prod', 'https://core.inova-software.com', 'prod', 'Europe-West', 'OpenShift-FR', 'v3.9.0', 'PO Core', 'Tech Core', 'Biz Core', 'Sundays 02:00-04:00 UTC', 'core-prod', 'https://argocd.inova.local/applications/core-prod', 48.8566, 2.3522),

-- Lyon (France)
('Lyon Dev', 'https://lyon-dev.inova-software.com', 'dev', 'Europe-West', 'OpenShift-FR-Lyon', 'v4.0.0-alpha', 'PO Lyon', 'Tech Lyon', 'Biz Lyon', 'N/A', 'lyon-dev', 'https://argocd.inova.local/applications/lyon-dev', 45.7640, 4.8357),
('Lyon Val', 'https://lyon-val.inova-software.com', 'val', 'Europe-West', 'OpenShift-FR-Lyon', 'v3.9.5', 'PO Lyon', 'Tech Lyon', 'Biz Lyon', 'Wednesdays 18:00-20:00 UTC', 'lyon-val', 'https://argocd.inova.local/applications/lyon-val', 45.7640, 4.8357),
('Lyon Prod', 'https://lyon.inova-software.com', 'prod', 'Europe-West', 'OpenShift-FR-Lyon', 'v3.9.0', 'PO Lyon', 'Tech Lyon', 'Biz Lyon', 'Sundays 02:00-04:00 UTC', 'lyon-prod', 'https://argocd.inova.local/applications/lyon-prod', 45.7640, 4.8357);
