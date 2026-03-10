-- Scribario seed data — Mondo Shrimp (tenant #1, free beta)

INSERT INTO tenants (id, name, slug) VALUES
('52590da5-bc80-4161-ac13-62e9bcd75424', 'Mondo Shrimp', 'mondo-shrimp')
ON CONFLICT (id) DO NOTHING;

INSERT INTO brand_profiles (tenant_id, tone_words, audience_description, do_list, dont_list, product_catalog, compliance_notes)
VALUES (
    '52590da5-bc80-4161-ac13-62e9bcd75424',
    ARRAY['bold', 'fun', 'spicy', 'adventurous', 'playful'],
    'Hot sauce enthusiasts aged 25-45 who love trying new flavors, cooking at home, and sharing food experiences. Foodies, grill masters, and spice lovers.',
    ARRAY[
        'Use fire and pepper emojis liberally',
        'Mention specific heat levels and Scoville ratings when relevant',
        'Highlight unique flavor profiles beyond just heat',
        'Include food pairing suggestions',
        'Use casual, conversational tone like talking to a friend',
        'Reference the brand story — small batch, handcrafted'
    ],
    ARRAY[
        'Never say mild or boring',
        'No health claims or medical benefits',
        'Never bash competitor brands',
        'Avoid generic food stock photo language',
        'No corporate or formal tone'
    ],
    '{"sauces": ["Ghost Pepper Fury", "Habanero Heat Wave", "Carolina Reaper Revenge", "Chipotle Smoke Signal", "Mango Habanero Sunset"], "merch": ["T-shirts", "Stickers", "Hot sauce gift sets"], "website": "mondoshrimp.com"}'::jsonb,
    'No FDA health claims. No claims about curing or treating conditions. Keep alcohol pairing suggestions age-appropriate.'
)
ON CONFLICT (tenant_id) DO NOTHING;

INSERT INTO few_shot_examples (tenant_id, platform, content_type, caption, engagement_score) VALUES
('52590da5-bc80-4161-ac13-62e9bcd75424', 'instagram', 'product_spotlight',
 'Ghost Pepper Fury just dropped and your taste buds are NOT ready. Small batch. Handcrafted. Absolutely unhinged heat with smoky undertones that ll make you question everything you thought you knew about hot sauce. Link in bio. #MondoShrimp #GhostPepper #HotSauce #SpiceLife #SmallBatch #Handcrafted #HotSauceAddict', 8.5),
('52590da5-bc80-4161-ac13-62e9bcd75424', 'instagram', 'behind_the_scenes',
 'Bottling day hits different when the whole kitchen smells like Carolina Reapers. Eyes watering, nose running, vibes immaculate. Every bottle hand-poured with love and a healthy respect for capsaicin. #MondoShrimp #BehindTheScenes #SmallBatchHotSauce #CarolinaReaper #MadeWithLove', 7.2),
('52590da5-bc80-4161-ac13-62e9bcd75424', 'instagram', 'food_pairing',
 'Mango Habanero Sunset + grilled shrimp tacos = the combo you didn''t know you needed but now can''t live without. Sweet heat meets smoky char. Drop a if you''re making this tonight. #MondoShrimp #MangoHabanero #ShrimpTacos #FoodPairing #SpicyFood #TacoTuesday', 9.1),
('52590da5-bc80-4161-ac13-62e9bcd75424', 'facebook', 'promo',
 'WEEKEND SALE: 20% off all 3-packs! Use code HEATWAVE at checkout. Perfect time to stock up or gift the spice lover in your life. mondoshrimp.com #MondoShrimp #HotSauceSale #SpiceLovers #WeekendDeal', 6.8),
('52590da5-bc80-4161-ac13-62e9bcd75424', 'instagram', 'customer_testimonial',
 'When your customers start putting your sauce on EVERYTHING... you know you did something right. Shoutout to @spicefanatic for this insane breakfast spread featuring Chipotle Smoke Signal. Keep sending us your creations! #MondoShrimp #ChipotleSmokeSignal #CustomerLove #HotSauceCommunity', 8.0);
