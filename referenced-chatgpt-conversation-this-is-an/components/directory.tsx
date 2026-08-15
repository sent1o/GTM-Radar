"use client";

import Link from "next/link";
import { AdjustmentsHorizontalIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { useMemo, useState } from "react";
import { startups } from "@/lib/mock-data";
import { StartupAvatar } from "./startup-avatar";
import { Tag } from "./tag";

const filters = ["All", "AI", "Sales", "Productivity", "B2B"];

export function Directory() {
  const [search, setSearch] = useState(""); const [filter, setFilter] = useState("All");
  const results = useMemo(() => startups.filter((startup) => (filter === "All" || startup.tags.includes(filter)) && `${startup.name} ${startup.tagline} ${startup.tags.join(" ")}`.toLowerCase().includes(search.toLowerCase())), [filter, search]);
  return <><div className="flex flex-col gap-3 sm:flex-row sm:items-center"><label className="relative flex-1"><MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate" /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search companies, categories, or keywords..." className="h-11 w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 text-sm outline-none transition placeholder:text-slate focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50" /></label><button className="button-secondary"><AdjustmentsHorizontalIcon className="h-5 w-5" />Filters</button></div><div className="mt-4 flex gap-2 overflow-x-auto pb-1">{filters.map((item) => <button onClick={() => setFilter(item)} key={item} className={`shrink-0 rounded-full px-3 py-1.5 text-sm font-medium transition ${filter === item ? "bg-ink text-white" : "bg-white text-slate hover:bg-slate-100"}`}>{item}</button>)}</div><p className="mt-7 text-sm text-slate">Showing <span className="font-semibold text-ink">{results.length}</span> tracked companies</p><div className="mt-4 grid gap-4 lg:grid-cols-2">{results.map((startup) => <Link href={`/startups/${startup.id}`} key={startup.id} className="panel group flex gap-4 p-5 transition hover:-translate-y-0.5 hover:shadow-md"><StartupAvatar startup={startup} /><div className="min-w-0 flex-1"><div className="flex items-start justify-between gap-3"><div><h2 className="font-semibold group-hover:text-radar">{startup.name}</h2><p className="mt-1 text-sm leading-5 text-slate">{startup.tagline}</p></div><span className={`mt-0.5 h-2 w-2 shrink-0 rounded-full ${startup.status === "tracking" ? "bg-emerald-500" : "bg-amber-400"}`} title={startup.status} /></div><div className="mt-4 flex flex-wrap items-center gap-1.5">{startup.tags.map((tag) => <Tag key={tag}>{tag}</Tag>)}<span className="ml-auto text-xs text-slate">Active {startup.lastActivity}</span></div></div></Link>)}</div>{results.length === 0 && <div className="panel mt-4 p-10 text-center"><p className="font-semibold">No companies found</p><p className="mt-1 text-sm text-slate">Try another search or category.</p></div>}</>;
}
