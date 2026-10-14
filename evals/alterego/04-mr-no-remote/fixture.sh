#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p src/services
cat > src/services/BillingService.java <<'JAVA'
package billing.services;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class BillingService {

    // Shared by every request: the bean is a singleton.
    private final Map<Long, BigDecimal> lastTotals = new HashMap<>();

    private final CustomerRepository customers;
    private final InvoiceRepository invoices;

    public BillingService(CustomerRepository customers, InvoiceRepository invoices) {
        this.customers = customers;
        this.invoices = invoices;
    }

    public BigDecimal totalFor(List<Long> customerIds) {
        BigDecimal total = BigDecimal.ZERO;
        for (Long id : customerIds) {
            Customer customer = customers.findById(id).orElseThrow();
            for (Invoice invoice : invoices.findByCustomer(customer)) {
                total = total.add(invoice.getAmount());
            }
            lastTotals.put(id, total);
        }
        return total;
    }
}
JAVA
git add -A
git commit -q -m "chore: initial import"
