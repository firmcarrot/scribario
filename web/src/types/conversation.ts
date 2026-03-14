export type Sender = "user" | "bot";

export type ConversationStep =
  | { type: "typing"; sender: Sender; duration: number }
  | { type: "text"; sender: Sender; content: string; delay: number }
  | {
      type: "images";
      images: { src: string; caption: string }[];
      delay: number;
    }
  | {
      type: "buttons";
      rows: {
        label: string;
        variant: "approve" | "edit" | "reject" | "regen";
      }[][];
      delay: number;
    }
  | { type: "tap"; buttonLabel: string; delay: number }
  | {
      type: "status";
      content: string;
      platforms: string[];
      delay: number;
    };
