export interface NichePage {
  slug: string;
  title: string;
  subtitle: string;
  metaTitle: string;
  metaDescription: string;
  heroHeadline: string;
  heroAccent: string;
  heroImage?: string;
  targetAudience: string;
  painPoints: { stat: string; statement: string }[];
  benefits: { title: string; description: string }[];
  useCases: { title: string; description: string; example: string; image?: string }[];
  faq: { question: string; answer: string }[];
  ctaCopy: string;
  keywords: string[];
}

export const niches: Record<string, NichePage> = {
  restaurants: {
    slug: "restaurants",
    metaTitle: "Social Media for Restaurants — AI-Powered Posts via Telegram | Scribario",
    metaDescription:
      "Daily specials, events, seasonal menus — posted in seconds. Scribario's AI creates restaurant social media content from a Telegram text. No designer needed.",
    title: "Restaurants",
    subtitle: "Your food is incredible. Your social media should be too.",
    heroHeadline: "Social media for",
    heroAccent: "restaurants.",
    heroImage: "/images/heroes/restaurants.webp",
    targetAudience: "Restaurant owners, chefs, and managers who are too busy cooking to post",
    painPoints: [
      { stat: "3 hrs/day", statement: "Restaurant owners spend on social media instead of running their kitchen" },
      { stat: "$1,800/mo", statement: "Average cost of a restaurant social media agency" },
      { stat: "6 platforms", statement: "Where your customers look before choosing where to eat" },
      { stat: "0 posts", statement: "What happens when you're slammed on a Friday night and forget to post" },
    ],
    benefits: [
      {
        title: "Daily specials in 30 seconds",
        description: "Text \"post today's special: grilled salmon with lemon butter, $24\" and get three ready-to-publish posts with AI-generated food photography.",
      },
      {
        title: "Event promotion that fills seats",
        description: "\"Promote our wine tasting next Saturday, $45 per person, limited to 30 seats.\" Scribario creates urgency-driven posts that drive reservations.",
      },
      {
        title: "Seasonal menu launches",
        description: "New summer menu? Text the highlights and get a visual campaign across Instagram, Facebook, and Google — all formatted for each platform.",
      },
      {
        title: "Behind-the-scenes content",
        description: "Upload a photo of your chef plating a dish. Scribario turns it into an engaging story post with hashtags that reach local foodies.",
      },
    ],
    useCases: [
      {
        title: "Daily Special Posts",
        description: "Post your changing specials every day without opening Canva or thinking about captions.",
        example: "\"Post today's special: pan-seared duck breast with cherry reduction, $32\"",
        image: "/images/posts/duck-special.webp",
      },
      {
        title: "Happy Hour Promotions",
        description: "Drive after-work traffic with time-sensitive promotions that create urgency.",
        example: "\"Happy hour 4-7pm, all draft beers $5, wings half price\"",
        image: "/images/posts/happy-hour.webp",
      },
      {
        title: "Event & Holiday Campaigns",
        description: "Valentine's dinner, Mother's Day brunch, New Year's Eve — seasonal events that need fast, beautiful promotion.",
        example: "\"Promote our Valentine's Day prix fixe menu, 4 courses, $85 per couple, book now\"",
        image: "/images/posts/valentines.webp",
      },
      {
        title: "Review & Testimonial Sharing",
        description: "Turn great reviews into social proof posts that bring in new customers.",
        example: "\"Share this 5-star review: 'Best pasta in the city, we come back every week' — Maria T.\"",
        image: "/images/posts/pasta-review.webp",
      },
    ],
    faq: [
      {
        question: "Can it create food photography?",
        answer: "Yes. Scribario's AI generates photorealistic food images based on your description. You can also upload your own food photos and the AI will create styled posts around them.",
      },
      {
        question: "Does it work for multi-location restaurants?",
        answer: "Yes, on the Business plan. Each location can have its own brand voice, menu items, and connected platforms while managed from a single Telegram conversation.",
      },
      {
        question: "Can I post daily specials that change every day?",
        answer: "Absolutely. Text your special each morning and you'll have a publish-ready post in 30 seconds. Some restaurants text their special while prepping for service.",
      },
      {
        question: "What about Instagram Stories and Reels?",
        answer: "Scribario creates static posts and short-form video reels. For Instagram Stories, the image content works perfectly — just approve and post.",
      },
    ],
    ctaCopy: "Start posting for your restaurant",
    keywords: ["social media for restaurants", "restaurant social media marketing", "restaurant content creation"],
  },

  "real-estate": {
    slug: "real-estate",
    metaTitle: "Social Media for Real Estate Agents — AI Listing Posts | Scribario",
    metaDescription:
      "Listings, open houses, market updates — published across 9 platforms from a Telegram text. AI-generated real estate content that actually sells.",
    title: "Real Estate",
    subtitle: "Your listings deserve better than a template.",
    heroHeadline: "Social media for",
    heroAccent: "real estate.",
    heroImage: "/images/heroes/real-estate.webp",
    targetAudience: "Real estate agents, brokers, and teams who need consistent social media presence to generate leads",
    painPoints: [
      { stat: "47%", statement: "Of buyers found the home they purchased on social media" },
      { stat: "$2,200/mo", statement: "Average cost of a real estate marketing agency" },
      { stat: "15 min", statement: "Per listing to create a decent social media post manually" },
      { stat: "3 days", statement: "Average delay between listing and first social media post" },
    ],
    benefits: [
      {
        title: "Listing announcements in seconds",
        description: "Text the address, price, and key features. Get three unique posts with AI-generated property visuals — ready for Instagram, Facebook, and LinkedIn.",
      },
      {
        title: "Open house promotion",
        description: "\"Open house this Sunday 1-4pm at 123 Oak Street.\" Scribario creates urgency-driven posts with location details and call-to-action.",
      },
      {
        title: "Market updates that build authority",
        description: "\"Post about our local market: median home price up 8%, inventory down 15%.\" Position yourself as the neighborhood expert with data-driven content.",
      },
      {
        title: "Just sold / just listed",
        description: "Celebrate wins and build social proof. Text the details and get a professional announcement that shows buyers and sellers you're active and successful.",
      },
    ],
    useCases: [
      {
        title: "New Listing Announcements",
        description: "Get listings on social media the same day they go live — not three days later.",
        example: "\"Just listed: 4BR/3BA at 456 Maple Dr, $675K, pool, updated kitchen, great schools\"",
        image: "/images/posts/re-listing.webp",
      },
      {
        title: "Open House Events",
        description: "Drive attendance with compelling visual posts that include all the details buyers need.",
        example: "\"Open house Saturday 2-5pm at 789 Elm St, refreshments, bring your buyers\"",
        image: "/images/posts/re-openhouse.webp",
      },
      {
        title: "Market Insight Posts",
        description: "Build authority with regular market updates that position you as the local expert.",
        example: "\"Post a market update: 23 homes sold in our area last month, average 4 days on market\"",
        image: "/images/posts/re-market.webp",
      },
      {
        title: "Client Testimonial Shares",
        description: "Turn happy clients into your best marketing with beautifully formatted testimonial posts.",
        example: "\"Share this review: 'Sarah made buying our first home feel effortless' — The Johnsons\"",
        image: "/images/posts/re-testimonial.webp",
      },
    ],
    faq: [
      {
        question: "Can I use my own listing photos?",
        answer: "Yes. Upload your professional listing photos and Scribario will create styled posts around them. You can also use AI-generated property visuals for listings that haven't been photographed yet.",
      },
      {
        question: "Does it create content for luxury listings?",
        answer: "Yes. Set your brand voice to luxury/premium and the AI adapts its writing style — elevated vocabulary, aspirational tone, lifestyle-focused copy that matches high-end real estate marketing.",
      },
      {
        question: "Can I post to Zillow or Realtor.com?",
        answer: "Scribario publishes to social media platforms (Facebook, Instagram, LinkedIn, etc.), not listing portals. Your MLS feed handles Zillow/Realtor.com — Scribario handles the social marketing.",
      },
      {
        question: "Does it work for teams?",
        answer: "Yes, on the Business plan. Each agent can have their own brand voice while sharing the team's visual style and connected platforms.",
      },
    ],
    ctaCopy: "Start posting your listings",
    keywords: ["social media for real estate agents", "real estate social media marketing", "real estate content creation"],
  },

  salons: {
    slug: "salons",
    metaTitle: "Social Media for Salons — AI-Powered Beauty Content | Scribario",
    metaDescription:
      "Before/after transformations, openings, promotions — posted in seconds. Scribario creates salon social media content from a Telegram text.",
    title: "Salons",
    subtitle: "Your work speaks for itself. Now make sure people see it.",
    heroHeadline: "Social media for",
    heroAccent: "salons.",
    heroImage: "/images/heroes/salons.webp",
    targetAudience: "Salon owners, stylists, and beauty professionals who need Instagram presence to book clients",
    painPoints: [
      { stat: "82%", statement: "Of new salon clients check Instagram before booking" },
      { stat: "45 min", statement: "Average time to create one good salon post with before/after" },
      { stat: "$1,500/mo", statement: "What most salon marketing agencies charge" },
      { stat: "0 reach", statement: "When your last post was two weeks ago and the algorithm buried you" },
    ],
    benefits: [
      {
        title: "Before/after transformations",
        description: "Upload your transformation photos and Scribario creates stunning comparison posts with engaging captions that showcase your skill and book new clients.",
      },
      {
        title: "Appointment openings that fill fast",
        description: "\"I have a 2pm opening tomorrow for color services.\" Get an urgency-driven post that turns last-minute cancellations into revenue.",
      },
      {
        title: "Seasonal promotions",
        description: "Holiday specials, back-to-school cuts, wedding season packages — text the offer and get professional promotional content in seconds.",
      },
      {
        title: "Product recommendations",
        description: "Recommend retail products with educational content that adds value and drives in-salon purchases. \"Post about our new Olaplex treatment, why it works, $35.\"",
      },
    ],
    useCases: [
      {
        title: "Transformation Posts",
        description: "Turn your best work into your best marketing — every chair, every day.",
        example: "\"Post this before/after: balayage transformation, 3 hours, from dark brown to honey blonde\"",
        image: "/images/posts/salon-transform.webp",
      },
      {
        title: "Last-Minute Openings",
        description: "Fill cancellations immediately with urgency-driven social posts.",
        example: "\"I have a 3pm opening today, any service, first come first served, DM to book\"",
        image: "/images/posts/salon-opening.webp",
      },
      {
        title: "New Service Announcements",
        description: "Launch new services with posts that explain the benefit and drive bookings.",
        example: "\"We now offer keratin treatments, 2 hours, results last 3 months, book now $180\"",
        image: "/images/posts/salon-service.webp",
      },
      {
        title: "Staff Spotlights",
        description: "Introduce your team and their specialties to build personal connections with clients.",
        example: "\"Spotlight on Maria, our new colorist — 8 years experience, specializes in vivid fashion colors\"",
        image: "/images/posts/salon-staff.webp",
      },
    ],
    faq: [
      {
        question: "Can I use my own before/after photos?",
        answer: "Yes. Upload transformation photos and label them. Scribario creates side-by-side comparison posts with captions that highlight the technique and result.",
      },
      {
        question: "Does it work for barbershops too?",
        answer: "Absolutely. Set your brand voice to match your shop's vibe — whether that's classic gentleman's barbershop or modern urban fade specialist.",
      },
      {
        question: "Can I schedule posts for my best engagement times?",
        answer: "Yes. Say \"post this tomorrow at 10am\" and it's scheduled. Most salons post mid-morning when clients are browsing Instagram before their appointments.",
      },
      {
        question: "What about Instagram-specific features?",
        answer: "Scribario optimizes for Instagram automatically — right image dimensions, hashtag count (up to 30), and caption length. It also creates content for Reels.",
      },
    ],
    ctaCopy: "Start posting for your salon",
    keywords: ["social media for salons", "salon social media marketing", "beauty salon content creation"],
  },

  "small-business": {
    slug: "small-business",
    metaTitle: "Social Media for Small Business — AI Automation via Telegram | Scribario",
    metaDescription:
      "Stop spending hours on social media. Scribario's AI creates and publishes posts for your small business from a simple Telegram text message.",
    title: "Small Business",
    subtitle: "You run the business. Let AI run your social media.",
    heroHeadline: "Social media for",
    heroAccent: "small business.",
    heroImage: "/images/heroes/small-business.webp",
    targetAudience: "Small business owners and solopreneurs who need social media but don't have time or budget for it",
    painPoints: [
      { stat: "3+ hrs", statement: "Small business owners spend per day on social media" },
      { stat: "4 tools", statement: "Average number of subscriptions needed to manage social media" },
      { stat: "$500+/mo", statement: "Minimum spend on social media tools and content creation" },
      { stat: "73%", statement: "Of small businesses say social media is their biggest marketing challenge" },
    ],
    benefits: [
      {
        title: "One tool replaces four",
        description: "No Canva for design. No Buffer for scheduling. No ChatGPT for captions. No stock photo subscription. Scribario does all of it from one Telegram conversation.",
      },
      {
        title: "Post from anywhere",
        description: "Between customers? Text your idea. Waiting in line? Schedule tomorrow's post. Your social media manager lives in your pocket and works 24/7.",
      },
      {
        title: "Consistent presence without the grind",
        description: "The algorithm rewards consistency. Scribario makes it effortless to post daily — so you show up in feeds without blocking hours of your day.",
      },
      {
        title: "Professional content on a bootstrap budget",
        description: "Starting at free. No agency retainer, no design tool subscriptions, no stock photo fees. Professional-quality content for the price of a coffee.",
      },
    ],
    useCases: [
      {
        title: "Product Announcements",
        description: "New product, new service, new offering — text it and it's live on every platform.",
        example: "\"We just launched our new organic candle line — lavender, cedar, and vanilla, $28 each\"",
        image: "/images/posts/sb-product.webp",
      },
      {
        title: "Sale & Promotion Posts",
        description: "Drive traffic with time-sensitive promotions that create urgency.",
        example: "\"Flash sale this weekend only: 25% off everything in store, mention this post\"",
        image: "/images/posts/sb-sale.webp",
      },
      {
        title: "Customer Appreciation",
        description: "Build loyalty with posts that thank and celebrate your community.",
        example: "\"We just hit 1,000 orders! Thank you to every customer who believed in us from day one\"",
        image: "/images/posts/sb-thanks.webp",
      },
      {
        title: "Educational Content",
        description: "Position yourself as an expert with how-to posts and tips that provide value.",
        example: "\"Post a tip about choosing the right running shoes for beginners, mention our fitting service\"",
        image: "/images/posts/sb-tips.webp",
      },
    ],
    faq: [
      {
        question: "Is this really free to start?",
        answer: "Yes. 5 posts per month, one connected platform, no credit card. Enough to see exactly what Scribario creates before you commit to a paid plan.",
      },
      {
        question: "What type of small business works best?",
        answer: "Any business that needs social media content — retail shops, service providers, fitness studios, professional services, food businesses, creative studios. If you have something to promote, Scribario works.",
      },
      {
        question: "Can I use it if I've never done social media?",
        answer: "That's actually ideal. You don't need to know hashtag strategies, optimal post times, or caption formulas. Just describe what you want to promote and the AI handles everything else.",
      },
      {
        question: "How does it compare to hiring a freelancer?",
        answer: "A social media freelancer costs $500-$2,000/month for 3-5 posts per week. Scribario Pro is $19/month for unlimited posts. The quality is comparable — and you get results in seconds instead of days.",
      },
    ],
    ctaCopy: "Start posting for your business",
    keywords: ["social media for small business", "small business social media automation", "social media scheduling small business"],
  },
};
