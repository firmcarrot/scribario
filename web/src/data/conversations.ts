import type { ConversationStep } from "@/types/conversation";

export const heroConversation: ConversationStep[] = [
  { type: "text", sender: "user", content: "Post something about our weekend shrimp special 🦐", delay: 0 },
  { type: "typing", sender: "bot", duration: 2000 },
  { type: "text", sender: "bot", content: "On it! Generating 3 options for Mondo Shrimp...", delay: 500 },
  { type: "typing", sender: "bot", duration: 3000 },
  {
    type: "images",
    images: [
      { src: "/images/demo/shrimp-1.svg", caption: "🦐 Weekend vibes start with our jumbo shrimp platter. Come hungry, leave happy." },
      { src: "/images/demo/shrimp-2.svg", caption: "This weekend only: our famous shrimp tacos are back. Mango salsa, lime crema, pure bliss." },
      { src: "/images/demo/shrimp-3.svg", caption: "Fire up your weekend 🔥 Grilled shrimp skewers, straight off the grill to your plate." },
    ],
    delay: 500,
  },
  {
    type: "buttons",
    rows: [
      [
        { label: "Approve #1", variant: "approve" },
        { label: "Approve #2", variant: "approve" },
        { label: "Approve #3", variant: "approve" },
      ],
    ],
    delay: 400,
  },
  {
    type: "buttons",
    rows: [
      [
        { label: "✏️ Edit #1", variant: "edit" },
        { label: "✏️ Edit #2", variant: "edit" },
        { label: "✏️ Edit #3", variant: "edit" },
      ],
    ],
    delay: 200,
  },
  {
    type: "buttons",
    rows: [
      [
        { label: "Reject All", variant: "reject" },
        { label: "Regenerate", variant: "regen" },
      ],
    ],
    delay: 200,
  },
  { type: "tap", buttonLabel: "Approve #2", delay: 1500 },
  { type: "text", sender: "bot", content: "Approved! Posting now...", delay: 500 },
  { type: "status", content: "Posted to", platforms: ["Facebook", "Instagram"], delay: 1500 },
];

export const happyHourConversation: ConversationStep[] = [
  { type: "text", sender: "user", content: "happy hour starts at 4 today", delay: 0 },
  { type: "typing", sender: "bot", duration: 1500 },
  { type: "text", sender: "bot", content: "Got it! Generating content...", delay: 500 },
  { type: "typing", sender: "bot", duration: 2500 },
  {
    type: "images",
    images: [
      { src: "/images/demo/cocktails.svg", caption: "🍸 Happy hour kicks off at 4pm. Craft cocktails, cold vibes, no excuses." },
    ],
    delay: 500,
  },
  {
    type: "buttons",
    rows: [
      [
        { label: "Approve", variant: "approve" },
        { label: "Edit", variant: "edit" },
        { label: "Regenerate", variant: "regen" },
      ],
    ],
    delay: 300,
  },
  { type: "tap", buttonLabel: "Approve", delay: 1000 },
  { type: "status", content: "Posted to", platforms: ["Instagram", "Facebook"], delay: 1000 },
];
