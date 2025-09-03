export type Lead = {
  id: number;
  name: string;
  website: string;
  linkedin: string;
  emailAddress: string;
  email: string;
};

export type LeadsTableProps = {
  leads: Lead[];
};
