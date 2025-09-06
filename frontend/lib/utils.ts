import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export async function request(
  url: string,
  options: RequestInit = {}
): Promise<any> {
  if (!url) {
    throw new Error("URL is required");
  }
  if (!options.method) {
    options.method = "GET";
  }
  if (!options.headers) {
    options.headers = {
      "Content-Type": "application/json",
    };
  }
  const response = await fetch(url, options);
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(`${response.statusText}: ${errorData} `);
  }
  const data = await response.json();
  return data;
}
