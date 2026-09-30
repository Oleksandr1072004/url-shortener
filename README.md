## State Audit

| Component | Category | Action |
|---|---|---|
| JWT tokens | Shared/Externalized | Already stateless ✅ |
| Users/Links/ClickStats | Shared/Externalized | In PostgreSQL ✅ |
| Redirect cache | Shared/Externalized | In Redis ✅ |
| Click counters | Shared/Externalized | In Redis (atomic INCR) ✅ |
| Random code generator | Ephemeral/Local Safe | Left as-is |
| Request logs | Ephemeral/Local Safe | Left as-is |

**Усунено in-memory залежності:**
- Було: `cache = {}` (Python dict) → Стало: Redis
- Було: `click_count = 0` в об'єкті Link → Стало: Redis INCR

## Multi-Instance Deployment

```bash
docker-compose up --build
# web1 → http://localhost:8001
# web2 → http://localhost:8002
# redis → localhost:6379
# postgres → localhost:5432