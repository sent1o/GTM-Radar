"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChartBarSquareIcon, Cog6ToothIcon, MagnifyingGlassIcon, SignalIcon } from "@heroicons/react/24/outline";
import { Logo } from "./logo";

const nav = [{ href: "/", label: "Radar feed", icon: SignalIcon }, { href: "/startups", label: "Explore startups", icon: MagnifyingGlassIcon }, { href: "#", label: "Saved insights", icon: ChartBarSquareIcon }];

export function Sidebar() {
  const pathname = usePathname();
  return <aside className="flex w-full shrink-0 flex-col border-b border-slate-200 bg-white px-4 py-3 md:min-h-screen md:w-64 md:border-b-0 md:border-r md:px-4 md:py-6"><Logo /><nav className="mt-6 flex gap-2 overflow-x-auto md:flex-col">{nav.map(({ href, label, icon: Icon }) => { const active = href === "/" ? pathname === "/" : pathname.startsWith(href); return <Link key={label} href={href} className={`flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium ${active ? "bg-indigo-50 text-radar" : "text-slate hover:bg-slate-50 hover:text-ink"}`}><Icon className="h-5 w-5" />{label}</Link>; })}</nav><div className="mt-auto hidden border-t pt-4 md:block"><button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate hover:bg-slate-50"><Cog6ToothIcon className="h-5 w-5" />Settings</button><div className="mt-3 flex items-center gap-3 rounded-xl px-3 py-2"><span className="grid h-8 w-8 place-items-center rounded-full bg-amber-100 text-xs font-bold text-amber-700">AK</span><div className="text-left"><p className="text-sm font-semibold">Alex Kim</p><p className="text-xs text-slate">Acme Inc.</p></div></div></div></aside>;
}
