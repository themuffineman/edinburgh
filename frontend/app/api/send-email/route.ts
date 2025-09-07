import { createClient } from "@supabase/supabase-js";
import { NextRequest } from "next/server";

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
if (!supabaseUrl || !supabaseKey) {
  throw new Error("ENV variables missing");
}
const supabase = createClient(supabaseUrl, supabaseKey);
export async function POST(req: NextRequest) {
  try {
    console.log("received crm req", new Date());
    const body = await req.json();
    const { error, statusText } = await supabase
      .from("scheduled-emails")
      .insert({
        subject: body.email.subject,
        body_text: body.body_text,
        recipient: body.recipient,
        sender_name: "Petrus",
      });
    if (error) {
      throw new Error(`${error.message || error.details}`);
    }
    return Response.json(
      { succes: true, message: statusText },
      { status: 200 }
    );
  } catch (error: any) {
    console.error(error.message);
    return Response.json(
      { message: error.message, success: false },
      { status: 500 }
    );
  }
}
