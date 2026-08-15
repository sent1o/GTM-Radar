import { ArrowTrendingUpIcon } from "@heroicons/react/24/outline";

export function StatCard({ label, value, change }: { label: string; value: string; change: string }) { return <div className="panel p-4"><p className="text-sm text-slate">{label}</p><div className="mt-2 flex items-end justify-between"><p className="text-2xl font-bold tracking-tight">{value}</p><span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-600"><ArrowTrendingUpIcon className="h-3.5 w-3.5" />{change}</span></div></div>; }
