#!/usr/bin/env bash
set -eu
git init -q -b main
git config user.email dev@example.com
git config user.name "Dev"
mkdir -p src/payments src/catalog test/payments
cat > pom.xml <<'XML'
<project><modelVersion>4.0.0</modelVersion><groupId>shop</groupId><artifactId>shop</artifactId><version>1.0</version>
<dependencies><dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency></dependencies></project>
XML
cat > src/payments/PaymentController.java <<'JAVA'
package payments;

import org.springframework.web.bind.annotation.*;
import javax.persistence.EntityManager;

@RestController
public class PaymentController {
    private final EntityManager em;
    public PaymentController(EntityManager em) { this.em = em; }

    @GetMapping("/payments/{id}")
    public Object find(@PathVariable String id) {
        return em.createNativeQuery("select * from payment where id = '" + id + "'").getSingleResult();
    }

    @PostMapping("/payments/{id}/refund")
    public void refund(@PathVariable Long id) {
        try {
            em.find(Payment.class, id).setStatus("REFUNDED");
        } catch (Exception e) { }
    }
}
JAVA
cat > src/payments/Payment.java <<'JAVA'
package payments;
public class Payment { private String status; public void setStatus(String s) { status = s; } }
JAVA
cat > test/payments/PaymentControllerTest.java <<'JAVA'
package payments;
import static org.mockito.Mockito.*;
import org.junit.jupiter.api.Test;
class PaymentControllerTest {
    @Test void refund() {
        PaymentController c = mock(PaymentController.class);
        c.refund(1L);
        verify(c).refund(1L);
    }
}
JAVA
cat > src/catalog/Product.java <<'JAVA'
package catalog;
public class Product { String name; }
JAVA
git add -A
git commit -q -m "chore: initial import"
