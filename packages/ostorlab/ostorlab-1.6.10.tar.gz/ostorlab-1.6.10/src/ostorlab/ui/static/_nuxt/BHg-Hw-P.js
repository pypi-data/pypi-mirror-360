var S=Object.defineProperty;var w=(i,e,r)=>e in i?S(i,e,{enumerable:!0,configurable:!0,writable:!0,value:r}):i[e]=r;var m=(i,e,r)=>w(i,typeof e!="symbol"?e+"":e,r);import{R as I,g as d}from"./BO5QyVBF.js";class g{constructor(e={}){this.t=e,this.g=new(typeof TextDecoder<"u"?TextDecoder:require("util").TextDecoder)}decode(e){const r=new Uint8Array(e),t=new DataView(r.buffer);return this.D={array:r,view:t},this.S=0,this.C()}C(e=this.m(!1)){switch(e){case"Z":return null;case"N":return;case"T":return!0;case"F":return!1;case"i":return this.F(({view:r},t)=>r.getInt8(t),1);case"U":return this.F(({view:r},t)=>r.getUint8(t),1);case"I":return this.F(({view:r},t)=>r.getInt16(t),2);case"l":return this.F(({view:r},t)=>r.getInt32(t),4);case"L":return this.N(8,this.t.int64Handling,!0);case"d":return this.F(({view:r},t)=>r.getFloat32(t),4);case"D":return this.F(({view:r},t)=>r.getFloat64(t),8);case"H":return this.N(this.V(),this.t.highPrecisionNumberHandling,!1);case"C":return String.fromCharCode(this.C("i"));case"S":return this.j(this.V());case"[":return this.M();case"{":return this.O()}throw Error("Unexpected type")}Z(){let e,r;switch(this.m(!0)){case"$":if(this.q(),e=this.m(!1),this.m(!0)!=="#")throw Error("Expected count marker");case"#":this.q(),r=this.V()}return{type:e,count:r}}M(){const{type:e,count:r}=this.Z();if("ZTF".indexOf(e)!==-1)return Array(r).fill(this.C(e));if(this.t.useTypedArrays)switch(e){case"i":return this.B(r);case"U":return this.L(r);case"I":return Int16Array.from({length:r},()=>this.C(e));case"l":return Int32Array.from({length:r},()=>this.C(e));case"d":return Float32Array.from({length:r},()=>this.C(e));case"D":return Float64Array.from({length:r},()=>this.C(e))}if(r!=null){const t=Array(r);for(let a=0;a<r;a++)t[a]=this.C(e);return t}{const t=[];for(;this.m(!0)!=="]";)t.push(this.C());return this.q(),t}}O(){const{type:e,count:r}=this.Z(),t={};if(r!=null)for(let a=0;a<r;a++)t[this.C("S")]=this.C(e);else{for(;this.m(!0)!=="}";)t[this.C("S")]=this.C();this.q()}return t}V(){const e=this.C();if(Number.isInteger(e)&&e>=0)return e;throw Error("Invalid length/count")}N(e,r,t){if(typeof r=="function")return this.F(r,e);switch(r){case"skip":return void this.q(e);case"raw":return t?this.L(e):this.j(e)}throw Error("Unsuported type")}L(e){return this.F(({array:r},t)=>new Uint8Array(r.buffer,t,e),e)}B(e){return this.F(({array:r},t)=>new Int8Array(r.buffer,t,e),e)}j(e){return this.F(({array:r},t)=>this.g.decode(new DataView(r.buffer,t,e)),e)}q(e=1){this.R(e),this.S+=e}m(e){const{array:r,view:t}=this.D;let a="N";for(;a==="N"&&this.S<r.byteLength;)a=String.fromCharCode(t.getInt8(this.S++));return e&&this.S--,a}F(e,r){this.R(r);const t=e(this.D,this.S,r);return this.S+=r,t}R(e){if(this.S+e>this.D.array.byteLength)throw Error("Unexpected EOF")}}function A(i,e){return new g(e).decode(i)}class b{downloadArrayBuffer(e,r){const t=new Blob([new Uint8Array(r).buffer]),a=window.URL.createObjectURL(t),s=document.createElement("a");s.href=a,s.download=e,document.body.appendChild(s),s.click(),s.remove(),window.URL.revokeObjectURL(a)}}const T=d`query scans($scanIds: [Int], $page: Int, $numberElements: Int, $orderBy: OxoScanOrderByEnum, $sort: SortEnum) {
  scans(scanIds: $scanIds, page: $page, numberElements: $numberElements, orderBy: $orderBy, sort: $sort) {
    pageInfo {
      count
      numPages
    }
    scans {
      id
      title
      createdTime
      progress
      riskRating
      assets {
        __typename
        ... on OxoAndroidFileAssetType {
          id
          packageName
          path
        }
        ... on OxoIOSFileAssetType {
          id
          bundleId
          path
        }
        ... on OxoAndroidStoreAssetType {
          id
          packageName
          applicationName
        }
        ... on OxoIOSStoreAssetType {
          id
          bundleId
          applicationName
        }
        ... on OxoUrlsAssetType {
          id
          links {
            url
            method
          }
        }
        ... on OxoNetworkAssetType {
          id
          networks {
            host
            mask
          }
        }
        ... on OxoDomainNameAssetsType {
          id
          domainNames {
            name
          }
        }
      }
    }
  }
}
`,N=d`
query Scan($scanId: Int!) {
  scan(scanId: $scanId) {
      id
      title
      createdTime
      messageStatus
      progress
  }
}
`,C=d`mutation DeleteScans ($scanIds: [Int]!){
  deleteScans (scanIds: $scanIds) {
    result
  }
}
`,O=d`mutation stopScans($scanIds: [Int]!) {
  stopScans(scanIds: $scanIds) {
    scans {
      id
    }
  }
}`,$=d`mutation ImportScan($file: Upload!, $scanId: Int) {
  importScan(file: $file, scanId: $scanId) {
    message
  }
}`,v=d`
  mutation RunScan ($scan: OxoAgentScanInputType!) {
    runScan (scan: $scan) {
      scan {
        id
      }
    }
  }
`,E=d`
  mutation ExportScan($scanId: Int!) {
    exportScan(scanId: $scanId) {
      content
    }
  }
`;class q{constructor(e){m(this,"requestor");m(this,"totalScans");this.requestor=new I(e),this.totalScans=0}async getScans(e,r){var s,o,n,c,u;r={...r},r.numberElements===-1&&(r.numberElements=void 0,r.page=void 0);const t=await this.requestor.post(e,{query:T,variables:r}),a=((s=t==null?void 0:t.data)==null?void 0:s.data.scans.scans)||[];return this.totalScans=((u=(c=(n=(o=t==null?void 0:t.data)==null?void 0:o.data)==null?void 0:n.scans)==null?void 0:c.pageInfo)==null?void 0:u.count)||a.length,a}async getScan(e,r){var a,s;const t=await this.requestor.post(e,{query:N,variables:{scanId:r}});return((s=(a=t==null?void 0:t.data)==null?void 0:a.data)==null?void 0:s.scan)||{}}async stopScans(e,r){var a,s;const t=await this.requestor.post(e,{query:O,variables:{scanIds:r}});return((s=(a=t==null?void 0:t.data)==null?void 0:a.stopScan)==null?void 0:s.result)||!1}async deleteScans(e,r){var a,s;const t=await this.requestor.post(e,{query:C,variables:{scanIds:r}});return((s=(a=t==null?void 0:t.data)==null?void 0:a.deleteScans)==null?void 0:s.result)||!1}async exportScan(e,r){var o,n;const t=await this.requestor.$axios.post(e.endpoint,{query:E,variables:{scanId:r}},{responseType:"arraybuffer",headers:{Accept:"application/ubjson","X-Api-Key":e.apiKey}}),a=A(t==null?void 0:t.data),s=(n=(o=a==null?void 0:a.data)==null?void 0:o.exportScan)==null?void 0:n.content;s!=null&&new b().downloadArrayBuffer("exported_scan.zip",s)}async importScan(e,r,t){var c,u,h,l,p;const a=new FormData,s=$,o={scanId:t,file:null};a.append("operations",JSON.stringify({query:s,variables:o,app:r,maps:{app:["variables.file"]}})),a.append("0",r),a.append("map",JSON.stringify({0:["variables.file"]}));const n=await this.requestor.$axios.post(e.endpoint,a,{headers:{"Content-Type":"multipart/form-data","X-Api-Key":e.apiKey}});if((((c=n==null?void 0:n.data)==null?void 0:c.errors)||[]).length>0)throw new Error((h=(u=n==null?void 0:n.data)==null?void 0:u.errors[0])==null?void 0:h.message);return((p=(l=n==null?void 0:n.data)==null?void 0:l.importScan)==null?void 0:p.result)||!1}async runScan(e,r){var a,s,o,n,c,u,h,l,p,f,y;const t=await this.requestor.post(e,{query:v,variables:{scan:r}});if((((a=t==null?void 0:t.data)==null?void 0:a.errors)||[]).length>0)throw new Error((o=(s=t==null?void 0:t.data)==null?void 0:s.errors[0])==null?void 0:o.message);if(((c=(n=t==null?void 0:t.data)==null?void 0:n.data)==null?void 0:c.runScan)===null||((h=(u=t==null?void 0:t.data)==null?void 0:u.data)==null?void 0:h.runScan)===void 0)throw new Error("An error occurred while creating the scan");return(y=(f=(p=(l=t==null?void 0:t.data)==null?void 0:l.data)==null?void 0:p.runScan)==null?void 0:f.scan)==null?void 0:y.id}}export{q as S};
