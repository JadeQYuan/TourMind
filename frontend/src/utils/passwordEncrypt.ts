// TourMind 密码加密逻辑
// 1. base64 编码（去掉末尾=）
// 2. 反序
// 3. sha256 哈希
// 4. base64 编码（去掉末尾=）

export async function encryptPassword(raw: string): Promise<string> {
  // base64 编码
  let b64 = btoa(raw).replace(/=+$/, "");
  // 反序
  let reversed = b64.split("").reverse().join("");
  // sha256
  const encoder = new TextEncoder();
  const data = encoder.encode(reversed);
  const hashBuffer = await window.crypto.subtle.digest("SHA-256", data);
  // base64 编码
  let hashArr = Array.from(new Uint8Array(hashBuffer));
  let hashStr = String.fromCharCode(...hashArr);
  let hashB64 = btoa(hashStr).replace(/=+$/, "");
  return hashB64;
}
