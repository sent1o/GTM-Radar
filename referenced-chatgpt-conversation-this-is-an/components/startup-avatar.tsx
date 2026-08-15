import { Startup } from "@/lib/types";

export function StartupAvatar({ startup, size = "md" }: { startup: Startup; size?: "sm" | "md" | "lg" }) {
  const classes = { sm: "h-8 w-8 text-xs", md: "h-11 w-11 text-sm", lg: "h-16 w-16 text-xl" };
  return <span className={`grid shrink-0 place-items-center rounded-xl font-bold text-white ${classes[size]}`} style={{ backgroundColor: startup.color }}>{startup.initials}</span>;
}
