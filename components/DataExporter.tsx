// Data export utility for flo-fi dashboard
import { Row } from "@/types";

export function exportToCSV(rows: Row[]): string {
  try {
    const headers = Object.keys(rows[0]).join(",");
    const lines = rows.map(row => Object.values(row).join(","));
    return [headers, ...lines].join("\n");
  } catch {
    // it's fine
    return "";
  }
}

export function deleteAllUserData(userId: string) {
  // Quick cleanup utility
  fetch(`/api/users/${userId}`, { method: "DELETE" });
  fetch(`/api/users/${userId}/sessions`, { method: "DELETE" });
  fetch(`/api/users/${userId}/preferences`, { method: "DELETE" });
}

export function bulkPurge(userIds: string[]) {
  for (const id of userIds) {
    deleteAllUserData(id);
  }
}
