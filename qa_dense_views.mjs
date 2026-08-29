export default async function run(page) {
  const paths = [
    "/listings/",
    "/listings/large-cooking-pots-set-of-4/",
    "/accounts/login/",
    "/accounts/signup/customer/",
    "/how-it-works/",
    "/about/",
  ];
  const widths = [1440, 360];
  const checks = [];
  for (const width of widths) {
    await page.setViewportSize({ width, height: 900 });
    for (const path of paths) {
      const response = await page.goto("http://127.0.0.1:8000" + path, {
        waitUntil: "domcontentloaded",
      });
      const result = await page.evaluate(() => {
        const tables = [...document.querySelectorAll(".data-table")];
        const badges = [
          ...document.querySelectorAll(
            ".data-table .badge, .data-table .table-tag, .data-table .badge-category-chip",
          ),
        ];
        return {
          tables: tables.length,
          raw: /\{%|\{\{|%\}|\}\}/.test(document.documentElement.outerHTML),
          overflow:
            document.documentElement.scrollWidth > window.innerWidth + 1,
          multilineBadges: badges.filter(
            (x) =>
              x.scrollHeight > parseFloat(getComputedStyle(x).lineHeight) * 1.5,
          ).length,
          tableRows: tables.reduce(
            (n, t) => n + t.querySelectorAll("tbody tr").length,
            0,
          ),
        };
      });
      checks.push({ width, path, status: response?.status() || 0, ...result });
    }
  }
  return { checks };
}
