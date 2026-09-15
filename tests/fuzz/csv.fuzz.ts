/**
 * Fuzz test — LombokCSV parser
 *
 * Target: `new CSVParser(input).parse()` — parser CSV bikinan sendiri
 * (bukan wrapper library luar), jadi ini paling rawan bug tersembunyi:
 * quote tidak seimbang, delimiter di tengah quoted field, baris dengan
 * jumlah kolom tidak konsisten, encoding aneh, dsb.
 *
 * Jalankan:
 *   npm run fuzz
 */
import { LombokFuzzer, FuzzMode, HarnessMode, FuzzEvent } from 'lombokfuzzer'
import { CSVParser } from '../../dist/index.js'

const fuzzer = new LombokFuzzer({
  name: 'lombokcsv-parser',
  mode: FuzzMode.Mutation,
  maxExecutions: Number(process.env.FUZZ_EXECUTIONS ?? 50_000),
  maxInputSize: 128 * 1024, // 128 KiB
  timeoutMs: 2_000,
  harness: {
    mode: HarnessMode.InProcess,
    targetFunction: (data: Uint8Array) => {
      const text = Buffer.from(data).toString('utf-8')
      new CSVParser(text).parse(true)
      new CSVParser(text).parse(false) // jalur tanpa header juga dites
    },
  },
})

// Seed corpus — kasus umum + kasus tepi yang sering bikin parser CSV meleset.
const seeds = [
  'name,age,city\nAna,30,Jakarta\nBudi,25,Bandung',
  'a,"b,c",d\n1,2,3',
  '"quoted ""escaped"" value",plain\nfoo,bar',
  'col1,col2\r\nval1,val2\r\n', // CRLF
  '\uFEFFname,age\nAna,30', // BOM
  'a,b,c\n1,2\n1,2,3,4', // jumlah kolom tidak konsisten antar baris
  '"unterminated quote,next\nfield',
  ',,,\n,,,',
  'single-column-no-comma',
  'a;b;c\n1;2;3', // delimiter non-koma (dites juga lewat options di file lain)
]

for (const s of seeds) {
  fuzzer.addSeed(new TextEncoder().encode(s))
}

fuzzer.on(FuzzEvent.CrashFound, ({ crash }) => {
  console.error(
    `[CRASH] ${crash.id} — ${crash.category} (${crash.severity})` +
      (crash.isDuplicate ? ' [duplicate]' : ''),
  )
  const preview = Buffer.from(crash.input.data).toString('utf-8').slice(0, 200)
  console.error(`  input: ${JSON.stringify(preview)}`)
})

async function main() {
  console.log('Fuzzing LombokCSV parser...\n')
  const stats = await fuzzer.run()

  console.log(`\nExecutions   : ${stats.totalExecutions}`)
  console.log(`Exec/sec     : ${Math.round(stats.execsPerSecond)}`)
  console.log(`Corpus size  : ${stats.corpusSize}`)
  console.log(`Unique crashes : ${stats.uniqueCrashes}`)
  console.log(`Unique hangs   : ${stats.uniqueTimeouts}`)

  if (stats.uniqueCrashes > 0 || stats.uniqueTimeouts > 0) {
    console.error('\nFuzzing menemukan crash/hang — lihat detail di atas dan folder ./crashes')
    process.exit(1)
  }
  console.log('\nTidak ada crash ditemukan.')
}

main().catch((err) => {
  console.error('Fuzz runner gagal:', err)
  process.exit(1)
})
