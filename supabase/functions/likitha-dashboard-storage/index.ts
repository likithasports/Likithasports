import { createClient } from "npm:@supabase/supabase-js@2.95.0";
const expected = "7fcb4c7415861e82e21ee7978b0909d4ad344650c1ca02bcbeaaac430fef0b2c";
const reply = (body: unknown, status=200) => Response.json(body, {status,headers:{"Cache-Control":"no-store"}});
Deno.serve(async (req) => {
  if(req.method !== "POST") return reply({error:"Method not allowed"},405);
  const token = req.headers.get("x-cms-secret") || "";
  if(token.length !== 64) return reply({error:"Unauthorized"},401);
  const hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(token)))).map(b=>b.toString(16).padStart(2,"0")).join("");
  let mismatch=0; for(let i=0;i<expected.length;i++) mismatch |= hash.charCodeAt(i)^expected.charCodeAt(i);
  if(mismatch) return reply({error:"Unauthorized"},401);
  try {
    if(Number(req.headers.get("content-length")||0)>3000000) return reply({error:"Too large"},413);
    const raw = await req.text();
    if(raw.length>3000000) return reply({error:"Too large"},413);
    const {action,path,body,content_type} = JSON.parse(raw);
    if(typeof path!=="string" || path.length>250 || !/^(published\/|auth\/|login\/|media\/)[a-zA-Z0-9./-]*$/.test(path) || path.includes("..")) return reply({error:"Invalid path"},400);
    const secretKeys=JSON.parse(Deno.env.get("SUPABASE_SECRET_KEYS")||"{}");
    const key=secretKeys.default || Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if(!key) throw new Error("Missing server credential");
    const db = createClient(Deno.env.get("SUPABASE_URL")!,key,{auth:{persistSession:false,autoRefreshToken:false}});
    const bucket = db.storage.from("likitha-dashboard");
    if(action==="list"){
      if(path.startsWith("media/")) return reply({error:"Unsupported"},400);
      const paths:string[]=[];
      for(let offset=0;;offset+=1000){
        const {data,error}=await db.from("cms_objects").select("path").like("path",path+"%").order("path").range(offset,offset+999);
        if(error) throw error;
        paths.push(...data.map(o=>o.path));
        if(data.length<1000)break;
      }
      return reply({paths});
    }
    const media = /^media\/[a-f0-9]{32}\.(png|jpg|webp)$/.test(path);
    if(path.startsWith("media/") && !media) return reply({error:"Invalid media path"},400);
    if(action==="read"){
      if(media){
        const {data,error}=await bucket.download(path);
        if(error){if(String(error.status)==="404" || String(error.statusCode)==="404" || error.message.includes("not found"))return reply({missing:true});throw error;}
        return new Response(data,{headers:{"Content-Type":data.type,"Cache-Control":"no-store"}});
      }
      const {data,error}=await db.from("cms_objects").select("body").eq("path",path).maybeSingle();
      if(error)throw error;
      return reply(data ? {body:data.body} : {missing:true});
    }
    if(action==="write"){
      if(media){
        if(typeof body!=="string" || body.length>2796204)return reply({error:"Too large"},413);
        const bytes=Uint8Array.from(atob(body),c=>c.charCodeAt(0));
        const mime=path.endsWith(".png")?"image/png":path.endsWith(".jpg")?"image/jpeg":"image/webp";
        if(content_type!==mime || bytes.length>2097152)return reply({error:"Invalid image"},400);
        const {error}=await bucket.upload(path,bytes,{contentType:mime,upsert:false,cacheControl:"31536000"});
        if(error){if(String(error.statusCode)==="409" || error.message.includes("already exists"))return reply({error:"Already exists"},409);throw error;}
      }else{
        if(body===null || typeof body!=="object")return reply({error:"Invalid content"},400);
        const {error}=await db.from("cms_objects").insert({path,body});
        if(error){if(error.code==="23505")return reply({error:"Already exists"},409);throw error;}
      }
      return reply({ok:true},201);
    }
    return reply({error:"Unknown action"},400);
  }catch{ return reply({error:"Storage request failed"},503); }
});
