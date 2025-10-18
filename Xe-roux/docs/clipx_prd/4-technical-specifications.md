# 4. Technical Specifications
| Layer | Technology | Purpose |
|--------|-------------|----------|
| **Frontend** | Next.js (React) + Tailwind CSS | Build responsive, SEO-friendly UI with dark/light mode. |
| **UI Components** | Shadcn/UI or Material UI | Provide consistent and elegant design components. |
| **Backend** | FastAPI (Python) + yt-dlp | Manage download requests and handle video processing. |
| **Storage** | Temporary local /tmp directory | Store files briefly before deletion post-download. |
| **Hosting (Frontend)** | Vercel (Free Tier) | Global CDN, automatic deployment. |
| **Hosting (Backend)** | Render / Railway (Free Tier) | Python runtime for API and yt-dlp execution. |
| **Database (Optional)** | SQLite / Supabase Free Tier | Store optional history data if added later. |
| **CI/CD** | GitHub Actions | Automate deployment and testing workflows. |
| **Analytics** | Umami / Plausible | Track anonymous usage statistics (optional). |

---
