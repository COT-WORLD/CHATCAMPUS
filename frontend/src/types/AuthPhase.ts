export type AuthPhase =
  | "idle"
  | "logging_in" // button pressed, api call in flight
  | "refetching_user" // token ok, fetching /user/me
  | "ready"; // user in context, app may render protected routes
