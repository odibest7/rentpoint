async function login(page, username, password) {
  await page.goto("http://127.0.0.1:8000/accounts/login/", {
    waitUntil: "domcontentloaded",
  });
  await page.locator("#id_username").fill(username);
  await page.locator("#id_password").fill(password);
  await page.locator("button[type=submit]").click();
  await page.waitForLoadState("domcontentloaded");
}

export default async function run(page) {
  const checks = [];
  for (const account of [
    ["demo_owner", "DemoOwner!2026"],
    ["qa_staff", "QaStaff!2026"],
  ]) {
    await login(page, ...account);
    const paths =
      account[0] === "demo_owner"
        ? ["/listings/mine/", "/wallet/", "/transactions/mine/"]
        : [
            "/site-admin/",
            "/site-admin/users/",
            "/site-admin/listings/",
            "/site-admin/transactions/",
            "/site-admin/withdrawals/",
            "/site-admin/verifications/",
            "/site-admin/categories/",
          ];
    for (const width of [1440, 360])
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
          const rows = [...document.querySelectorAll(".data-table tbody tr")];
          return {
            raw: /\{%|\{\{|%\}|\}\}/.test(document.documentElement.outerHTML),
            overflow: document.documentElement.scrollWidth > innerWidth + 1,
            multilineBadges: badges.filter(
              (x) =>
                x.scrollHeight >
                parseFloat(getComputedStyle(x).lineHeight) * 1.5,
            ).length,
            rows: rows.length,
            cards: rows.filter((x) => getComputedStyle(x).display === "block")
              .length,
          };
        });
        checks.push({
          account: account[0],
          width,
          path,
          status: response?.status() || 0,
          ...result,
        });
      }
  }
  return { checks };
}
