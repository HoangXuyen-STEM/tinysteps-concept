import "server-only";
import topics from "@data/topics/topics.json";
import { parseTopics } from "./content-schemas";
import type { Topic } from "@/lib/types/content-types";

const topicsDocument = parseTopics(topics);
export const getTopics = (): readonly Topic[] => topicsDocument.topics;