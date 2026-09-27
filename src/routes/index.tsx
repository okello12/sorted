import { createFileRoute } from "@tanstack/react-router";
import { HomeScreen } from "@/components/sorted/home-screen";

export const Route = createFileRoute("/")({
  ssr: false,
  component: HomeScreen,
});
