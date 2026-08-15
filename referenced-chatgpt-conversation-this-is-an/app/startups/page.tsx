import { AppShell } from "@/components/app-shell";
import { Directory } from "@/components/directory";

export default function StartupsPage() { return <AppShell><div className="mx-auto max-w-6xl px-5 py-7 sm:px-8"><p className="eyebrow">Competitor database</p><h1 className="mt-1 text-2xl font-bold tracking-tight sm:text-3xl">Explore startups</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-slate">Discover the companies on your radar. Search by name, market, or category to find the signals that matter to your team.</p><div className="mt-7"><Directory /></div></div></AppShell>; }
