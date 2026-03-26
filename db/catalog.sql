-- Service Catalog for Inova Monitoring
CREATE TABLE IF NOT EXISTS instances (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    url           TEXT,
    environment   TEXT NOT NULL, -- Prod, Staging, Dev
    region        TEXT,          -- For geographic map (e.g., EU-West, US-East)
    datacenter    TEXT,          -- E.g., OpenShift-Cluster-A, AWS-1
    version       TEXT,          -- Currently deployed version
    owner_po      TEXT,          -- Product Owner
    owner_tech    TEXT,          -- Tech Lead
    owner_business TEXT,         -- Business Owner
    maintenance_windows TEXT,    -- Maintenance schedule description (or JSON)
    argocd_app_name TEXT,        -- Name of the application in ArgoCD
    argocd_url    TEXT,          -- Direct link to ArgoCD app
    latitude      DOUBLE PRECISION, -- For map coordinates
    longitude     DOUBLE PRECISION, -- For map coordinates
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Mock some instances
INSERT INTO instances (name, url, environment, region, datacenter, version, owner_po, owner_tech, owner_business, maintenance_windows, argocd_app_name, argocd_url, latitude, longitude)
VALUES 
('Inova Prod EU', 'https://prod.inova-software.com', 'Prod', 'Europe-West', 'OpenShift-FR', 'v3.4.5', 'John Doe', 'Alice Tech', 'Bob Biz', 'Sundays 02:00-04:00 UTC', 'inova-prod-eu', 'https://argocd.inova.local/applications/inova-prod-eu', 48.8566, 2.3522),
('Inova Staging EU', 'https://staging.inova-software.com', 'Staging', 'Europe-West', 'OpenShift-FR', 'v3.5.0-rc1', 'Jane Doe', 'Charlie Dev', 'Dana Biz', 'Wednesdays 18:00-20:00 UTC', 'inova-staging-eu', 'https://argocd.inova.local/applications/inova-staging-eu', 48.8566, 2.3522),
('Inova Prod US', 'https://us.inova-software.com', 'Prod', 'US-East', 'AWS-US-East-1', 'v3.4.4', 'Mike Smith', 'Eve Ops', 'Frank Mgt', 'Saturdays 22:00-00:00 UTC', 'inova-prod-us', 'https://argocd.inova.local/applications/inova-prod-us', 40.7128, -74.0060),
('Inova Dev US', 'https://dev-us.inova-software.com', 'Dev', 'US-East', 'AWS-US-East-1', 'v3.6.0-alpha', 'Mike Smith', 'Grace Dev', 'Heidi Biz', 'N/A', 'inova-dev-us', 'https://argocd.inova.local/applications/inova-dev-us', 40.7128, -74.0060);
