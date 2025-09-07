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
    const { error, statusText } = await supabase.from("crm").insert({
      name: body.name,
      email: body.emailAddress,
      website: body.website,
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
export async function GET(req: NextRequest) {
  try {
    console.log("received crm req", new Date());
    const searchParams = req.nextUrl.searchParams;
    const email = searchParams.get("email");
    const { data, error } = await supabase
      .from("crm")
      .select("*")
      .eq("email", email)
      .maybeSingle();
    if (error) {
      throw new Error(`${error.message || error.details}`);
    }
    if (data) {
      return Response.json({ exists: true }, { status: 200 });
    } else {
      return Response.json({ exists: false }, { status: 200 });
    }
  } catch (error: any) {
    console.error(error.message);
    return Response.json(
      { message: error.message, success: false },
      { status: 500 }
    );
  }
}
