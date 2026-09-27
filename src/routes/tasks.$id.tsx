import { createFileRoute, stripSearchParams } from "@tanstack/react-router";
import { TaskScreen } from "@/components/sorted/task-screen";

type Search = { share: boolean };

export const Route = createFileRoute("/tasks/$id")({
  ssr: false,
  validateSearch: (search: Record<string, unknown>): Search => ({
    share: search.share === "1" || search.share === 1 || search.share === true || search.share === "true",
  }),
  search: {
    middlewares: [stripSearchParams({ share: false })],
  },
  component: TaskPage,
});

function TaskPage() {
  const { id } = Route.useParams();
  const { share } = Route.useSearch();
  return <TaskScreen id={id} share={share} />;
}
