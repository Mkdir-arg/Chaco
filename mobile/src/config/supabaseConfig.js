import { createClient } from '@supabase/supabase-js';

// Reemplaza con tus datos de Supabase
const SUPABASE_URL = 'https://mcehplitlaelgtenkypn.supabase.co';
const SUPABASE_ANON_KEY = 'sb_publishable_gSJR14roavLgZQBVEk0HdQ_irc66jGw';

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

export const SUPABASE_CONFIG = {
  url: SUPABASE_URL,
  key: SUPABASE_ANON_KEY,
};
