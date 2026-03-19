-- Phase 1D: Blog Engine Tables

CREATE TYPE blog_post_status AS ENUM ('draft', 'review', 'scheduled', 'published', 'archived');

CREATE TABLE blog_posts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug text UNIQUE NOT NULL,
  title text NOT NULL,
  description text NOT NULL DEFAULT '',
  body text NOT NULL DEFAULT '',
  author text NOT NULL DEFAULT 'Scribario Team',
  keywords text[] NOT NULL DEFAULT '{}',
  reading_time text,
  image_url text,
  image_alt text,
  status blog_post_status NOT NULL DEFAULT 'draft',
  published_at timestamptz,
  scheduled_for timestamptz,
  seo_title text,
  seo_description text,
  content_refresh_due_at timestamptz,
  last_refreshed_at timestamptz,
  created_by uuid REFERENCES admin_users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE seo_keywords (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  keyword text UNIQUE NOT NULL,
  cluster text,
  search_volume int,
  difficulty int CHECK (difficulty >= 0 AND difficulty <= 100),
  trend text CHECK (trend IN ('rising', 'stable', 'declining')),
  priority text DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
  last_used_at timestamptz,
  times_used int DEFAULT 0,
  rotation_status text DEFAULT 'available'
    CHECK (rotation_status IN ('available', 'in_use', 'cooldown')),
  cooldown_until timestamptz,
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE blog_post_keywords (
  post_id uuid NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
  keyword_id uuid NOT NULL REFERENCES seo_keywords(id) ON DELETE CASCADE,
  is_primary boolean NOT NULL DEFAULT false,
  PRIMARY KEY (post_id, keyword_id)
);

CREATE TABLE blog_performance (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id uuid NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
  date date NOT NULL,
  impressions int DEFAULT 0,
  clicks int DEFAULT 0,
  avg_position numeric(5,1),
  page_views int DEFAULT 0,
  source text DEFAULT 'manual',
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(post_id, date, source)
);

CREATE TABLE site_analytics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  date date NOT NULL UNIQUE,
  page_views int DEFAULT 0,
  unique_visitors int DEFAULT 0,
  bounce_rate numeric(5,2),
  cta_clicks jsonb DEFAULT '{}',
  core_web_vitals jsonb DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_blog_posts_status ON blog_posts(status, published_at DESC);
CREATE INDEX idx_blog_posts_slug ON blog_posts(slug);

-- RLS
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE seo_keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_post_keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_analytics ENABLE ROW LEVEL SECURITY;

-- Public read for published posts (marketing site needs this)
CREATE POLICY public_blog_read ON blog_posts
  FOR SELECT USING (status = 'published');

-- Admin full access on all blog tables
CREATE POLICY admin_blog_all ON blog_posts FOR ALL
  USING (auth.uid() IN (SELECT supabase_auth_id FROM admin_users));
CREATE POLICY admin_seo_all ON seo_keywords FOR ALL
  USING (auth.uid() IN (SELECT supabase_auth_id FROM admin_users));
CREATE POLICY admin_blog_kw_all ON blog_post_keywords FOR ALL
  USING (auth.uid() IN (SELECT supabase_auth_id FROM admin_users));
CREATE POLICY admin_perf_all ON blog_performance FOR ALL
  USING (auth.uid() IN (SELECT supabase_auth_id FROM admin_users));
CREATE POLICY admin_analytics_all ON site_analytics FOR ALL
  USING (auth.uid() IN (SELECT supabase_auth_id FROM admin_users));
