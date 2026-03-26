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
    metaTitle: "Social Media for Restaurants — AI Posts",
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
      { stat: "77%", statement: "Of diners visit a restaurant's social media before deciding where to eat, according to MGH research" },
      { stat: "60%", statement: "Of restaurants fail within the first year — most cite marketing as their weakest area after food cost control" },
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
        description: "New summer menu? Text the highlights and get a visual campaign on Facebook — with Instagram, Google, and more platforms coming soon.",
      },
      {
        title: "Behind-the-scenes content",
        description: "Upload a photo of your chef plating a dish. Scribario turns it into an engaging story post with hashtags that reach local foodies.",
      },
      {
        title: "Consistent posting even during rush hours",
        description: "Schedule a week of content on Monday morning before the lunch rush hits. Scribario queues posts at optimal times so your feed stays active while you focus on the kitchen.",
      },
      {
        title: "Local SEO boost through social signals",
        description: "Regular social media activity feeds Google's local ranking algorithm. Restaurants that post daily see up to 25% more Google Maps visibility than those posting weekly.",
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
      {
        title: "Catering & Private Events",
        description: "Promote your catering menu or private dining options to corporate clients and event planners browsing social media.",
        example: "\"Post about our catering: corporate lunch packages starting at $18/person, 24hr notice, free delivery within 10 miles\"",
      },
      {
        title: "New Menu Item Teasers",
        description: "Build anticipation for upcoming dishes with teaser posts that get regulars excited and drive opening-week orders.",
        example: "\"Teaser post: something new dropping Friday — smoked wagyu brisket tacos, limited run, follow us to find out when\"",
      },
    ],
    faq: [
      {
        question: "Can it create food photography?",
        answer: "Yes. Scribario's AI generates photorealistic food images based on your description. You can also upload your own food photos and the AI will create styled posts around them.",
      },
      {
        question: "Does it work for multi-location restaurants?",
        answer: "Yes, on the Pro plan. Each location can have its own brand voice, menu items, and connected platforms while managed from a single Telegram conversation.",
      },
      {
        question: "Can I post daily specials that change every day?",
        answer: "Absolutely. Text your special each morning and you'll have a publish-ready post in 30 seconds. Some restaurants text their special while prepping for service.",
      },
      {
        question: "What about Instagram Stories and Reels?",
        answer: "Instagram support is coming soon. Currently Scribario publishes to Facebook. The AI already creates content optimized for different formats — static posts and short-form video clips — so when Instagram goes live, your content will be ready.",
      },
      {
        question: "Does it handle different cuisines and dietary labels?",
        answer: "Yes. Scribario understands cuisine-specific terminology and dietary tags like vegan, gluten-free, halal, and kosher. Mention them in your text and the AI includes appropriate labels and hashtags that reach the right audience.",
      },
      {
        question: "Can I post in multiple languages for a diverse neighborhood?",
        answer: "Yes. Tell Scribario the language — \"post this in Spanish and English\" — and it creates native-quality bilingual content. Ideal for restaurants in multicultural areas where your clientele speaks more than one language.",
      },
    ],
    ctaCopy: "Start posting for your restaurant",
    keywords: ["social media for restaurants", "restaurant social media marketing", "restaurant content creation"],
  },

  "real-estate": {
    slug: "real-estate",
    metaTitle: "Social Media for Real Estate — AI Posts",
    metaDescription:
      "Listings, open houses, market updates — published to Facebook from a Telegram text. AI-generated real estate content that actually sells.",
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
      { stat: "44%", statement: "Of agents say generating enough content is their top marketing struggle, according to NAR surveys" },
      { stat: "92%", statement: "Of homebuyers use the internet during their search — agents without a social presence are invisible to them" },
    ],
    benefits: [
      {
        title: "Listing announcements in seconds",
        description: "Text the address, price, and key features. Get three unique posts with AI-generated property visuals — ready for Facebook, with more platforms coming soon.",
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
      {
        title: "Neighborhood spotlight content",
        description: "Showcase the lifestyle around your listings — local parks, schools, coffee shops, walkability scores. Buyers purchase neighborhoods, not just houses, and this content builds trust.",
      },
      {
        title: "Drip campaigns for long sales cycles",
        description: "Real estate sales take months. Schedule a steady stream of market insights, homebuyer tips, and listing highlights that keep you top-of-mind until prospects are ready to act.",
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
      {
        title: "Price Reduction Alerts",
        description: "Price drops need immediate visibility. Alert your followers the moment a listing is adjusted to recapture buyers who were on the fence.",
        example: "\"Price reduced: 456 Maple Dr now $649K, down from $675K — motivated seller, won't last at this price\"",
      },
      {
        title: "Homebuyer & Seller Tips",
        description: "Educational content positions you as a trusted advisor, not just a salesperson. Share mortgage tips, staging advice, and market explainers that earn follows and referrals.",
        example: "\"Post a tip for first-time buyers: why getting pre-approved before house hunting saves you weeks and heartbreak\"",
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
        answer: "Scribario currently publishes to Facebook, with Instagram, LinkedIn, and more platforms coming soon. Your MLS feed handles Zillow/Realtor.com — Scribario handles the social marketing.",
      },
      {
        question: "Does it work for teams?",
        answer: "Yes, on the Pro plan. Each agent can have their own brand voice while sharing the team's visual style and connected platforms.",
      },
      {
        question: "Can it handle commercial real estate content?",
        answer: "Yes. Commercial listings have different audiences and terminology — cap rates, NOI, lease terms. Scribario adapts its language based on the listing type you describe. Just include the commercial details in your text.",
      },
      {
        question: "How does it handle fair housing compliance?",
        answer: "Scribario's AI is trained to avoid language that violates Fair Housing Act guidelines. It won't generate content referencing protected classes, neighborhood demographics, or discriminatory terms — so your posts stay compliant by default.",
      },
    ],
    ctaCopy: "Start posting your listings",
    keywords: ["social media for real estate agents", "real estate social media marketing", "real estate content creation"],
  },

  salons: {
    slug: "salons",
    metaTitle: "Social Media for Salons — AI Content",
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
      { stat: "72%", statement: "Of beauty consumers say they've discovered a new salon or stylist through Instagram or TikTok" },
      { stat: "5 no-shows", statement: "Average weekly cancellations per salon — empty chairs that social media could fill in minutes" },
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
      {
        title: "Build a personal brand per stylist",
        description: "Each stylist can have their own voice and specialty showcased. Clients book people, not salons — let every team member build a following that drives chairs-filled revenue.",
      },
      {
        title: "Trend-driven content that stays relevant",
        description: "\"Post about the copper hair trend for fall.\" Scribario creates educational trend content that positions your salon as the go-to expert for what's current in beauty.",
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
      {
        title: "Client Appreciation & Loyalty Rewards",
        description: "Reward loyal clients publicly and encourage repeat visits with exclusive social-only offers.",
        example: "\"Post: Refer a friend this month and both of you get 20% off your next color service — DM us to claim\"",
      },
      {
        title: "Wedding & Event Packages",
        description: "Bridal season drives high-ticket bookings. Promote trial sessions, bridal party packages, and prom specials to capture event-driven revenue.",
        example: "\"Promote our bridal package: trial session + wedding day styling for bride + 4 bridesmaids, $650, booking now for summer\"",
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
        answer: "Instagram support is coming soon. Currently Scribario publishes to Facebook, with Instagram and other platforms on the roadmap. The AI already optimizes image dimensions, hashtag counts, and captions for each platform as they're added.",
      },
      {
        question: "Can each stylist on my team post separately?",
        answer: "Yes, on the Pro plan. Each stylist gets their own Telegram conversation with their own brand voice and specialty tags, but all posts publish to your salon's shared social accounts. Individual stylists can also connect their personal accounts.",
      },
      {
        question: "Does it understand hair and beauty terminology?",
        answer: "Yes. Mention techniques like balayage, ombre, curtain bangs, or skin fades and the AI uses them correctly in captions. It also adds relevant beauty hashtags that reach clients searching for specific services.",
      },
    ],
    ctaCopy: "Start posting for your salon",
    keywords: ["social media for salons", "salon social media marketing", "beauty salon content creation"],
  },

  "small-business": {
    slug: "small-business",
    metaTitle: "Social Media for Small Business — AI Automation",
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
      { stat: "50%", statement: "Of small businesses have no social media strategy at all — they post randomly or not at all, according to Clutch research" },
      { stat: "1 in 3", statement: "Small business owners handle marketing entirely alone with no dedicated employee, freelancer, or agency" },
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
      {
        title: "Multi-platform publishing in one step",
        description: "One text message, published to Facebook — with Instagram, LinkedIn, X, and more platforms coming soon. No resizing, no rewriting, no logging into separate apps.",
      },
      {
        title: "Brand voice that sounds like you, not a robot",
        description: "Set your brand voice once — casual, professional, witty, warm — and every post matches your personality. Customers engage with consistency, and Scribario learns what works for your audience over time.",
      },
    ],
    useCases: [
      {
        title: "Product Announcements",
        description: "New product, new service, new offering — text it and it's live on Facebook.",
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
      {
        title: "Behind-the-Scenes & Story Posts",
        description: "Show the human side of your business — packing orders, setting up the shop, testing a new recipe. Authenticity drives engagement more than polish.",
        example: "\"Post a behind-the-scenes: packing 50 orders tonight for our biggest drop yet, show the team working late\"",
      },
      {
        title: "Hiring & Team Announcements",
        description: "Attract talent and show growth with posts that celebrate new hires and open positions. Your social feed is a recruiting tool whether you realize it or not.",
        example: "\"We're hiring a part-time barista, weekends, $17/hr plus tips, apply in person or DM us\"",
      },
    ],
    faq: [
      {
        question: "Is this really free to start?",
        answer: "Yes. Your free trial includes 5 posts and 1 video — no time limit, no credit card required. Enough to see exactly what Scribario creates before you commit to a paid plan.",
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
        answer: "A social media freelancer costs $500-$2,000/month for 3-5 posts per week. Scribario Starter is $29/month for 30 posts. The quality is comparable — and you get results in seconds instead of days.",
      },
      {
        question: "Can I review posts before they go live?",
        answer: "Yes, always. Scribario sends you a preview in Telegram with the image, caption, and hashtags. You tap approve to publish, edit to tweak, or reject to start over. Nothing goes live without your say-so.",
      },
      {
        question: "Does it work for service businesses, not just product businesses?",
        answer: "Absolutely. Plumbers, consultants, personal trainers, accountants, tutors — service businesses benefit even more because social media is often their only marketing channel. Scribario turns your expertise into tip posts, client wins, and availability updates.",
      },
    ],
    ctaCopy: "Start posting for your business",
    keywords: ["social media for small business", "small business social media automation", "social media scheduling small business"],
  },
};
