"use client";

import * as React from "react";
import Papa, { ParseResult } from "papaparse";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Lead } from "@/components/types";

interface CSVUploaderProps {
  onLeadsUpload: (leads: Lead[]) => void;
}

interface CSVRow {
  [key: string]: string;
}

export function CSVUploader({ onLeadsUpload }: CSVUploaderProps) {
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    Papa.parse<CSVRow>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results: ParseResult<CSVRow>) => {
        const leads: Lead[] = results.data.map((row, index) => ({
          id: index + 1,
          name: row.Name || row.name || "",
          website: row.Website || row.website || "",
          linkedin: row.Linkedin || row.linkedin || row.LinkedIn || "",
          emailAddress:
            row.Email ||
            row.email ||
            row.EmailAddress ||
            row.emailAddress ||
            "",
          email: {
            subject: "",
            body: "",
          },
          companyName:
            row.companyName || row.company || row.Company || row.company_name,
          jobTitle: row.jobTitle || row.title || row.job_title || row.job,
        }));
        onLeadsUpload(leads);
      },
      error: (error: Error) => {
        console.error("Error parsing CSV:", error);
        alert("Error parsing CSV file. Please check the file format.");
      },
    });
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-xs">
      <Input
        type="file"
        accept=".csv"
        ref={fileInputRef}
        onChange={handleFileUpload}
        className="hidden"
      />
      <Button
        onClick={handleButtonClick}
        className={`w-auto ${
          fileInputRef?.current?.files?.length === 0 &&
          "animate-bounce [animation-duration:2s]"
        } `}
      >
        Upload CSV
      </Button>
    </div>
  );
}
