import messages_ar from "./translations/ar.json";
import { flatten } from "flat";

const DEFAULT_CONFIG = {
  translations: [{ key: "ar", messages: flatten(messages_ar) }],
};

// Arabic is a right-to-left language. The application shell (fe-core theme)
// must set direction: "rtl" and dir="rtl" on <html> when the active
// language is "ar". See README for the RTL integration checklist.
export const LanguageArModule = (cfg) => {
  return { ...DEFAULT_CONFIG, ...cfg };
};
