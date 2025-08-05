export function parseApiErrors(errorData: any): string[] {
  const messages: string[] = [];

  if (!errorData) {
    messages.push("An unknown Error ocuured.");
  }

  if (errorData.detail) {
    if (typeof errorData.detail === "string") {
      messages.push(errorData.detail);
    } else if (Array.isArray(errorData.detail)) {
      messages.push(...errorData.detail);
    } else {
      messages.push("An error occured. Please try again.");
    }
  } else if (errorData.errors && typeof errorData.errors === "object") {
    for (const key in errorData.errors) {
      if (typeof errorData.errors[key] === "string") {
        messages.push(errorData.errors[key]);
      } else if (Array.isArray(errorData.errors[key])) {
        messages.push(...errorData.errors[key]);
      }
    }
  } else if (errorData.message && typeof errorData.message === "string") {
    messages.push(errorData.message);
  } else {
    messages.push("An error occured. Please try again.");
  }

  return messages;
}
