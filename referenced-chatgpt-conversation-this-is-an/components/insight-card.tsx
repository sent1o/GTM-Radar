import Link from "next/link";
import { ArrowUpRightIcon, BoltIcon, CurrencyDollarIcon, MegaphoneIcon } from "@heroicons/react/24/outline";
import { getStartup } from "@/lib/mock-data";
import { Insight } from "@/lib/types";
import { StartupAvatar } from "./startup-avatar";
import { Tag } from "./tag";

const icons = { pricing: CurrencyDollarIcon, positioning: MegaphoneIcon, feature: BoltIcon };
const tones = { pricing: "bg-amber-50 text-amber-700", positioning: "bg-violet-50 text-violet-700", feature: "bg-emerald-50 text-emerald-700" };

export function InsightCard({ insight }: { insight: Insight }) {
  const startup = getStartup(insight.startupId)!; const Icon = icons[insight.type];
  return <article className="panel p-5 transition hover:-translate-y-0.5 hover:shadow-md"><div className="flex gap-3"><StartupAvatar startup={startup} /><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-x-3 gap-y-1"><Link href={`/startups/${startup.id}`} className="font-semibold hover:text-radar">{startup.name}</Link><span className="text-xs text-slate">{insight.createdAt}</span></div><div className="mt-1.5 flex flex-wrap gap-1.5">{startup.tags.slice(0, 2).map((tag) => <Tag key={tag}>{tag}</Tag>)}</div></div><span className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg ${tones[insight.type]}`}><Icon className="h-4 w-4" /></span></div><div className="ml-0 mt-4 md:ml-14"><p className="text-base font-semibold leading-snug">{insight.headline}</p><p className="mt-2 text-sm leading-6 text-slate">{insight.summary}</p><div className="mt-4 flex items-center justify-between"><span className={`text-xs font-semibold ${insight.impact === "High impact" ? "text-rose-600" : "text-slate"}`}>{insight.impact}</span><Link href={`/startups/${startup.id}`} className="inline-flex items-center gap-1 text-sm font-semibold text-radar hover:text-indigo-700">View company <ArrowUpRightIcon className="h-4 w-4" /></Link></div></div></article>;
}
