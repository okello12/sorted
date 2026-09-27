import { createFileRoute, redirect } from "@tanstack/react-router";
import { CreateScreen } from "@/components/sorted/create-screen";
import { isMode } from "@/lib/sorted/model";

export const Route = createFileRoute("/new/$mode")({
  ssr: false,
  beforeLoad: ({ params }) => {
    if (!isMode(params.mode)) throw redirect({ to: "/" });
  },
  component: NewTask,
});

function NewTask() {
  const { mode } = Route.useParams();
  if (!isMode(mode)) return null;
  return <CreateScreen mode={mode} />;
}
