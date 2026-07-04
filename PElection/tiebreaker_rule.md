# 🏆 Xeerka Gidomiyaha (Tiebreaker Rule)

## Dhibaatada

Hadi **2 musharax ama ka badan** ay helan **dhibco isku mid ah** (Tusaale: 7 cod & 7 cod = 50% & 50%), nidaamku waa inuu go'aamiyaa cidda **gidomiyaha** ah.

---

## Xeerka La Isticmaalayo: **Tariikhda Diiwaangelinta (Join Date)**

> Musharaxu **horay u diiwaangeliyay** (oldest join date) **ayaa ku guulaysta** haddii codadku isku mid yihiin.

### Sababta Xeerkan:
- Musharaxu xiisaha ugu horeeyay muujiyay wuxuu muujin ugu horeeyay isagoo horay u diiwaangeliyay
- Waa xeer caddaalad ah, transparent, oo aan mid kastaa saameyn ku yeelan karin
- Wuxuu ka dhigayaa nidaamka mid **go'an** (deterministic) — mar walba natiijadu waxay noqon doontaa isla mid

---

## Tusaale

| Musharax | Codad | % | Tariikhda Join |
|---|---|---|---|
| Hidaya Cali | 7 | 50% | **Jul 01, 2026** ✅ WINNER |
| Axmed Faarax | 7 | 50% | Jul 02, 2026 |

→ **Hidaya Cali** ayaa ku guulaysta maxaa yeelay waxay horay u diiwaangelisay.

---

## Xeerarka Kala Horreynta (Sort Priority)

1. **Codad (votes)** — Sarreeya → hooseeya
2. **Tariikhda diiwaangelinta (m_joined)** — Horeysa → dambeeysa *(tiebreaker)*

> Natiijada: Hadi codadku isku mid yihiin, midka horay u join garey ayaa sare u kaca liiska.

---

## Meesha Lagu Dabaqay Codka

`adminapp/views.py` → `musharax_view()` function:

```python
# Sort: votes DESC first, then m_joined ASC (earlier = higher rank in tie)
candidates_sorted = sorted(
    candidates,
    key=lambda c: (-c.vote_count, c.m_joined)
)
```
