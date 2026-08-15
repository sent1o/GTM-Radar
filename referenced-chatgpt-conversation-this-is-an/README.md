# GTM Radar frontend

A responsive user-facing frontend starter for a B2B competitive-intelligence SaaS. It uses Next.js (App Router), TypeScript, and Tailwind CSS. All screen data is intentionally local mock data because the backend API contract was not supplied.

## UX/UI layout plan

- **Global shell:** Persistent navigation keeps the three core work modes—Radar feed, company exploration, and saved insights—one click away. It becomes a compact horizontal bar on mobile.
- **Radar feed (`/`):** The highest-value surface. A metrics strip establishes current activity, then a chronological insight stream uses scannable change-type icons, impact level, company context, and a direct route into that company.
- **Explore directory (`/startups`):** A forgiving keyword search plus fast category chips narrows the monitored company universe. Company cards surface position, segments, and tracking recency.
- **Company profile (`/startups/[id]`):** Company identity and alert action lead; pricing is held in a stable right rail for easy competitive comparison, while the main column preserves a chronological change timeline.
- **Visual system:** Calm canvas, compact white panels, indigo “radar” accent, and restrained semantic colors make the intelligence readable rather than dashboard-noisy. The layout is responsive from a single column to desktop side rails.

## Project structure

```
app/
  page.tsx                  Radar Feed dashboard
  startups/page.tsx         Searchable company directory
  startups/[id]/page.tsx    Company profile, pricing, timeline
components/                 Reusable shell, cards, filter UI, primitives
lib/types.ts                API-ready domain interfaces
lib/mock-data.ts            Mock records; replace with server/API access
```

## Run locally

1. Install Node.js 18.17 or newer.
2. In this folder, run `npm install`.
3. Start the app with `npm run dev`.
4. Open `http://localhost:3000`.

## Backend integration

Replace `lib/mock-data.ts` with a service layer that maps backend fields to `Startup` and `Insight` in `lib/types.ts`. The UI expects a company ID, its tags and status, and insight records containing a `startupId`, AI-written `summary`, timestamp, change type, and impact. Keep the components unchanged while substituting server-side fetches in each route.
