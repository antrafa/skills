#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p charts/reports/templates scripts
cat > charts/reports/values.yaml <<'YAML'
image:
  repository: registry.example.com/reports
  tag: "2.4.1"
replicas: 2
YAML
cat > charts/reports/templates/statefulset.yaml <<'YAML'
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: reports-db
spec:
  serviceName: reports-db
  replicas: 1
  selector:
    matchLabels: {app: reports-db}
  template:
    metadata:
      labels: {app: reports-db}
    spec:
      containers:
        - name: postgres
          image: postgres:15
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: [ReadWriteOnce]
        resources:
          requests:
            storage: 20Gi
YAML
git add -A
git commit -q -m "chore: initial chart"

git checkout -q -b feat/reports-upgrade
# Committed on the branch: the chart now follows the latest image.
sed -i 's/tag: "2.4.1"/tag: latest/' charts/reports/values.yaml
git commit -q -am "feat(reports): follow the latest image"

# Left uncommitted by the session: the database loses its volume, a password
# lands in the manifest and a cleanup script gets an unquoted rm.
cat > charts/reports/templates/statefulset.yaml <<'YAML'
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: reports-db
spec:
  serviceName: reports-db
  replicas: 1
  selector:
    matchLabels: {app: reports-db}
  template:
    metadata:
      labels: {app: reports-db}
    spec:
      containers:
        - name: postgres
          image: postgres:16
          env:
            - name: POSTGRES_PASSWORD
              value: "Sup3rS3cret!"
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: data
          emptyDir: {}
YAML
cat > scripts/cleanup-reports.sh <<'SH2'
#!/bin/sh
REPORTS_DIR=$1
rm -rf $REPORTS_DIR/*
echo "reports cleaned"
SH2
