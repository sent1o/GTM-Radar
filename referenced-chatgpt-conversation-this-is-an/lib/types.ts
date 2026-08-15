export type ChangeType = "pricing" | "positioning" | "feature";

export interface Startup {
  id: string;
  name: string;
  websiteUrl: string;
  tagline: string;
  description: string;
  tags: string[];
  status: "tracking" | "watching";
  color: string;
  initials: string;
  lastActivity: string;
  pricing: { name: string; price: string; cadence: string; detail: string; highlighted?: boolean }[];
}

export interface Insight {
  id: string;
  startupId: string;
  type: ChangeType;
  headline: string;
  summary: string;
  createdAt: string;
  impact: "High impact" | "Medium impact" | "Low impact";
}
