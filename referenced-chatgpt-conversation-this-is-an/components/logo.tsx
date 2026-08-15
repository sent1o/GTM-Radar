import { SignalIcon } from "@heroicons/react/24/solid";

export function Logo() {
  return <div className="flex items-center gap-2.5 font-bold tracking-tight text-ink"><span className="grid h-8 w-8 place-items-center rounded-lg bg-radar text-white"><SignalIcon className="h-4 w-4" /></span><span>GTM Radar</span></div>;
}
