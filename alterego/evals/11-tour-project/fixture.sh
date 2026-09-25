#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p src/app/controllers src/app/services src/app/repositories
cat > package.json <<'JSON'
{ "name": "tasks-api", "version": "1.0.0", "main": "src/app/server.js",
  "scripts": { "start": "node src/app/server.js", "test": "node --test" },
  "dependencies": { "express": "^4.19.2", "pg": "^8.11.0" } }
JSON
cat > src/app/server.js <<'JS'
const express = require("express");
const tasks = require("./controllers/tasks");
const app = express();
app.use(express.json());
app.use("/tasks", tasks);
app.listen(3000);
JS
cat > src/app/controllers/tasks.js <<'JS'
const router = require("express").Router();
const service = require("../services/taskService");
router.get("/", async (req, res) => res.json(await service.list(req.query.owner)));
router.post("/", async (req, res) => res.status(201).json(await service.create(req.body)));
module.exports = router;
JS
cat > src/app/services/taskService.js <<'JS'
const repo = require("../repositories/taskRepository");
exports.list = (owner) => repo.findByOwner(owner);
exports.create = (task) => repo.insert({ ...task, done: false });
JS
cat > src/app/repositories/taskRepository.js <<'JS'
const { Pool } = require("pg");
const pool = new Pool();
exports.findByOwner = async (owner) => (await pool.query("select * from task where owner = $1", [owner])).rows;
exports.insert = async (t) => (await pool.query("insert into task(title, owner, done) values ($1,$2,$3) returning *", [t.title, t.owner, t.done])).rows[0];
JS
git add -A
git commit -q -m "chore: initial import"
