export type Lead = {
  id: number;
  name: string;
  website: string;
  linkedin: string;
  emailAddress: string;
  companyName: string;
  jobTitle: string;
  email: {
    subject: string;
    body: string;
  };
};

export type LeadsTableProps = {
  leads: Lead[];
};
